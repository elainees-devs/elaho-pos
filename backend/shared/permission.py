from django.core.cache import cache
from rest_framework.permissions import BasePermission


def _resolve_perm_codes(user):
    role = getattr(user, "role", None)
    if role is None:
        return frozenset()

    cache_key = f"perm_codes_{role.pk}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    codes = frozenset(
        role.permissions.values_list("permission__code", flat=True)
    )
    cache.set(cache_key, codes, timeout=300)
    return codes


def HasPermission(permission_code):
    class _HasPermission(BasePermission):
        message = "You do not have permission to perform this action."

        def has_permission(self, request, view):
            user = request.user

            if not user or not user.is_authenticated:
                return False

            if getattr(user, "role", None) is None:
                return False

            return permission_code in _resolve_perm_codes(user)

    return _HasPermission


def HasRoleLevel(min_level):
    class _HasRoleLevel(BasePermission):
        message = "Your role level is insufficient."

        def has_permission(self, request, view):
            user = request.user

            if not user or not user.is_authenticated:
                return False

            role = getattr(user, "role", None)
            if role is None:
                return False

            return role.level >= min_level

    return _HasRoleLevel


class IsSuperAdmin(BasePermission):
    message = "Only Super Administrators can perform this action."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        role = getattr(user, "role", None)
        if role is None:
            return False

        return role.name.lower() == "superadmin"