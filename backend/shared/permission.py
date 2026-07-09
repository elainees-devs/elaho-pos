# shared/permissions.py

from rest_framework.permissions import BasePermission


def HasPermission(permission_code):
    class _HasPermission(BasePermission):
        message = "You do not have permission to perform this action."

        def has_permission(self, request, view):
            user = request.user

            if not user or not user.is_authenticated:
                return False

            role = getattr(user, "role", None)
            if role is None:
                return False

            return role.permissions.filter(code=permission_code).exists()

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

        return role.name == "SuperAdmin"