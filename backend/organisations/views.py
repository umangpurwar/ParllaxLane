from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Organisation, OrganisationMember
from django.contrib.auth import get_user_model
import uuid
from .models import OrganisationInvite

User = get_user_model()


# 1. Create Organisation
class CreateOrganisationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")
        slug = request.data.get("slug")

        if not name or not slug:
            return Response({"error": "name and slug required"}, status=400)

        if Organisation.objects.filter(slug=slug).exists():
            return Response({"error": "slug already exists"}, status=400)

        org = Organisation.objects.create(
            name=name,
            slug=slug,
            owner=request.user
        )

        # add creator as owner member
        OrganisationMember.objects.create(
            organisation=org,
            user=request.user,
            role="owner"
        )

        # set active org
        request.user.current_organisation = org
        request.user.save()

        return Response({"status": "created", "org": slug})


# 2. List my organisations
class MyOrganisationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = OrganisationMember.objects.filter(user=request.user)

        data = [
            {
                "name": m.organisation.name,
                "slug": m.organisation.slug,
                "role": m.role
            }
            for m in memberships
        ]

        return Response(data)


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

        return Response({"status": "switched", "org": slug})


#  4. Invite member 


class InviteMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        org = get_object_or_404(Organisation, slug=slug)

        # check admin
        if not org.members.filter(
            user=request.user,
            role__in=["owner", "admin"]
        ).exists():
            return Response({"error": "Forbidden"}, status=403)

        email = request.data.get("email")
        role = request.data.get("role", "candidate")

        if not email:
            return Response({"error": "email required"}, status=400)

        #  ALWAYS create invite first
        invite = OrganisationInvite.objects.create(
            organisation=org,
            email=email,
            role=role,
            token=str(uuid.uuid4())
        )

        #  THEN check if user exists
        user = User.objects.filter(email=email).first()

        if user:
            OrganisationMember.objects.get_or_create(
                organisation=org,
                user=user,
                defaults={"role": role}
            )
            invite.accepted = True
            invite.save()

            return Response({"status": "user added directly"})

        
        return Response({
            "status": "invite created",
            "invite_token": invite.token
        })

# 5. List members (admin only)
class OrganisationMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        org = get_object_or_404(Organisation, slug=slug)

        if not org.members.filter(
            user=request.user,
            role__in=["owner", "admin"]
        ).exists():
            return Response({"error": "Forbidden"}, status=403)

        members = org.members.select_related("user")

        data = [
            {
                "username": m.user.username,
                "email": m.user.email,
                "role": m.role
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

        OrganisationMember.objects.get_or_create(
            organisation=invite.organisation,
            user=request.user,
            defaults={"role": invite.role}
        )

        invite.accepted = True
        invite.save()

        return Response({"status": "joined organisation"})