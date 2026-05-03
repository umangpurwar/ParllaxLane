from rest_framework.permissions import BasePermission
from django.core.cache import cache

def get_membership(user):
    if not user or not user.is_authenticated:
        return None

    org = getattr(user, "current_organisation", None)
    if not org:
        return None

    membership_key = f"membership:{user.id}:{org.id}"
    plan_key = f"org_plan:{org.id}"

    membership = cache.get(membership_key)

    if membership is not None:
        return membership

    membership = user.memberships.select_related("organisation", "user").filter(
        organisation=org,
        is_active=True
    ).first()

    cache.set(membership_key, membership, timeout=300)

    if cache.get(plan_key) is None:
        cache.set(plan_key, org.plan, timeout=300)

    return membership


class IsOrgMember(BasePermission):
    def has_permission(self, request, view):
        return get_membership(request.user) is not None


class IsOrgAdmin(BasePermission):
    def has_permission(self, request, view):
        membership = get_membership(request.user)
        if not membership:
            return False
        return membership.role in ["owner", "admin"]


class IsOrgInvigilator(BasePermission):
    def has_permission(self, request, view):
        membership = get_membership(request.user)
        if not membership:
            return False
        return membership.role in ["owner", "admin", "invigilator"]


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)