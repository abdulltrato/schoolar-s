from django.conf import settings
from rest_framework.permissions import BasePermission


class RoleBasedAccessPermission(BasePermission):
    """
    ViewSets may define `allowed_roles` as:
    {
        "*": {"role_a", "role_b"},
        "list": {...},
        "create": {...},
    }
    """

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        profile = getattr(user, "school_profile", None)
        if profile is not None and getattr(profile, "deleted_at", None) is not None:
            profile = None
        if profile is None:
            return not getattr(settings, "REQUIRE_USER_PROFILE", False)
        if not profile.active:
            return False

        allowed_roles = getattr(view, "allowed_roles", None)
        if not allowed_roles:
            return True

        action = getattr(view, "action", None)
        roles = allowed_roles.get(action)
        if roles is None:
            roles = allowed_roles.get("*")

        if roles is None:
            return True

        return profile.role in roles
