from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Organisation, OrganisationMember,OrganisationInvite
from django.contrib.auth import get_user_model
import uuid
from django.utils.text import slugify
from rest_framework.decorators import api_view, permission_classes
from core.permissions import IsOrgAdmin
from django.core.cache import cache
from django.utils.timezone import now
from datetime import timedelta

User = get_user_model()


# 1. Create Organisation
class CreateOrganisationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")

        if not name:
            return Response(
                {"error": "Organisation name is required"},
                status=400
            )

        base_slug = slugify(name)
        slug = base_slug
        counter = 1

        while Organisation.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        org = Organisation.objects.create(
            name=name,
            slug=slug,
            owner=request.user
        )

        OrganisationMember.objects.create(
            organisation=org,
            user=request.user,
            role="owner"
        )

        request.user.current_organisation = org
        request.user.save()

        return Response({
            "status": "created",
            "slug": org.slug,
            "name": org.name,
            "plan": org.plan,
            "role": "owner"
        })
    

# 2. List my organisations
class MyOrganisationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = (
            OrganisationMember.objects
            .filter(user=request.user, is_active=True)
            .select_related("organisation")
        )

        data = [
            {
                "name": m.organisation.name,
                "slug": m.organisation.slug,
                "role": m.role
            }
            for m in memberships
        ]

        return Response({
            "count": len(data),
            "organisations": data
        })


#  3. Switch organisation
class SwitchOrganisationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        membership = OrganisationMember.objects.filter(
            user=request.user,
            organisation__slug=slug
        ).first()

        if not membership:
            return Response({"error": "Not a member"}, status=403)

        request.user.current_organisation = membership.organisation
        request.user.save()

        return Response({
            "status": "switched",
            "slug": membership.organisation.slug,
            "name": membership.organisation.name,
            "plan": membership.organisation.plan,
            "role": membership.role
        })

#  4. Invite member 


class InviteMemberView(APIView):
    permission_classes = [IsOrgAdmin]

    def post(self, request, slug):
        org = get_object_or_404(Organisation, slug=slug)

        email = request.data.get("email")
        role = request.data.get("role", "candidate")
        expiry_days = request.data.get("expiry_days")

        if not email:
            return Response({"error": "email required"}, status=400)

        if role not in ["admin", "invigilator", "candidate"]:
            return Response({"error": "invalid role"}, status=400)

        if role == "admin" and org.plan == "free":
            return Response({"error": "upgrade to pro to add admins"}, status=403)

        if role == "admin":
            admin_count = org.members.filter(role="admin").count()
            if admin_count >= 3:
                return Response({"error": "admin limit reached"}, status=403)

        expires_at = None
        if expiry_days:
            try:
                expiry_days = int(expiry_days)

                if expiry_days < 1 or expiry_days > 30:
                    return Response(
                        {"error": "expiry_days must be between 1 and 30"},
                        status=400
                    )

                expires_at = now() + timedelta(days=expiry_days)

            except:
                return Response({"error": "Invalid expiry_days"}, status=400)

        invite = OrganisationInvite.objects.create(
            organisation=org,
            email=email,
            role=role,
            token=str(uuid.uuid4()),
            expires_at=expires_at
        )

        user = User.objects.filter(email=email).first()

        if user:
            member, _ = OrganisationMember.objects.get_or_create(
                organisation=org,
                user=user,
                defaults={"role": role}
            )

            invite.accepted = True
            invite.save()

            cache.delete(f"membership:{user.id}:{org.id}")

            return Response({
                "status": "user added directly",
                "org_slug": org.slug,
                "org_name": org.name,
                "org_plan": org.plan,
                "org_role": member.role
            })

        return Response({
            "status": "invite created",
            "invite_link": f"/api/organisations/accept/{invite.token}/",
            "expires_at": invite.expires_at
        })


# 5. List members (admin only)
class OrganisationMembersView(APIView):
    permission_classes = [IsOrgAdmin]

    def get(self, request, slug):
        org = get_object_or_404(Organisation, slug=slug)

        members = org.members.select_related("user")

        data = [
            {
                "username": m.user.username,
                "email": m.user.email,
                "role": m.role,
                "joined_at": m.joined_at
            }
            for m in members
        ]

        return Response(data)
    
class AcceptInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, token):
        invite = get_object_or_404(OrganisationInvite, token=token)

        if invite.accepted:
            return Response({"error": "Already accepted"}, status=400)

        # CHECKS MUST COME FIRST
        if invite.is_revoked:
            return Response({"error": "Invite revoked"}, status=400)

        if invite.expires_at and now() > invite.expires_at:
            return Response({"error": "Invite expired"}, status=400)
        
        if request.user.email != invite.email:
            return Response({"error": "this invite is not for your email"}, status=403)

        # ONLY AFTER VALIDATION then create member
        member, _ = OrganisationMember.objects.get_or_create(
            organisation=invite.organisation,
            user=request.user,
            defaults={"role": invite.role}
        )

        invite.accepted = True
        invite.save()

        # set active organisation
        request.user.current_organisation = invite.organisation
        request.user.save()

        return Response({
            "status": "joined",
            "org_slug": invite.organisation.slug,
            "org_name": invite.organisation.name,
            "org_plan": invite.organisation.plan,
            "org_role": member.role
        })


@api_view(['DELETE'])
@permission_classes([IsOrgAdmin])
def remove_member(request, slug, username):

    org = get_object_or_404(Organisation, slug=slug)

    member = get_object_or_404(
        OrganisationMember,
        organisation=org,
        user__username=username
    )

    # prevent removing owner
    if member.role == "owner":
        return Response({"error": "cannot remove owner"}, status=400)

    # prevent removing yourself
    if member.user == request.user:
        return Response({"error": "cannot remove yourself"}, status=400)

    cache.delete(f"membership:{member.user.id}:{org.id}")

    member.delete()

    return Response({"status": "member removed"})


@api_view(['PATCH'])
@permission_classes([IsOrgAdmin])
def update_member_role(request, slug, username):

    org = get_object_or_404(Organisation, slug=slug)

    member = get_object_or_404(
        OrganisationMember,
        organisation=org,
        user__username=username
    )

    new_role = request.data.get("role")

    if new_role not in ["admin", "invigilator", "candidate"]:
        return Response({"error": "invalid role"}, status=400)

    if member.role == "owner":
        return Response({"error": "cannot change owner role"}, status=400)

    # plan check
    if org.plan == "free" and new_role == "admin":
        return Response({"error": "upgrade to pro to add admins"}, status=403)

    # pro admin limit (3 admins max)
    if new_role == "admin":
        admin_count = org.members.filter(role="admin").exclude(user=member.user).count()
        if admin_count >= 3:
            return Response({"error": "admin limit reached"}, status=403)

    member.role = new_role
    member.save()

    cache.delete(f"membership:{member.user.id}:{org.id}")

    return Response({"status": "role updated"})


@api_view(['GET'])
@permission_classes([IsOrgAdmin])
def list_invites(request, slug):

    org = get_object_or_404(Organisation, slug=slug)

    invites = OrganisationInvite.objects.filter(
        organisation=org,
        accepted=False,
        is_revoked=False
    ).order_by('-created_at')

    data = []

    for invite in invites:
        data.append({
            "email": invite.email,
            "role": invite.role,
            "token": invite.token,
            "expires_at": invite.expires_at,
            "created_at": invite.created_at
        })

    return Response(data)

@api_view(['POST'])
@permission_classes([IsOrgAdmin])
def revoke_invite(request, slug, token):

    org = get_object_or_404(Organisation, slug=slug)

    invite = get_object_or_404(
        OrganisationInvite,
        token=token,
        organisation=org
    )

    if invite.accepted:
        return Response({"error": "cannot revoke accepted invite"}, status=400)

    if invite.is_revoked:
        return Response({"error": "invite already revoked"}, status=400)

    invite.is_revoked = True
    invite.save()

    return Response({"status": "invite revoked"})