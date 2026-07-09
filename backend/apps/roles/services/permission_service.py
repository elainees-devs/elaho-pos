from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import Http404

from shared.constants import PermissionCode

from ..models import Permission

class PermissionService:
    """
    Service responsible for permission management.

    Responsibilities:
    - Create permission
    - Update permission
    - Delete permission
    - Assign permission to role
    - Retrieve permissions
    """

    @staticmethod
    def _validate_permission_code(code: str | PermissionCode) -> PermissionCode:
        """
        Ensure the permission code is one of the canonical codes.
        """
        try:
            return PermissionCode(code)
        except ValueError:
            raise ValidationError("Invalid permission code.")

    @staticmethod
    def _validate_unique_name(name: str, exclude_id: int | None = None) -> None:
        """
        Ensure the permission name is unique.
        """
        queryset = Permission.objects.filter(name=name)

        if exclude_id is not None:
            queryset = queryset.exclude(pk=exclude_id)

        if queryset.exists():
            raise ValidationError("Permission already exists.")

    @staticmethod
    def _validate_unique_code(code: str, exclude_id: int | None = None) -> None:
        """
        Ensure the permission code is unique.
        """
        queryset = Permission.objects.filter(code=code)

        if exclude_id is not None:
            queryset = queryset.exclude(pk=exclude_id)

        if queryset.exists():
            raise ValidationError("Permission code already exists.")

    @staticmethod
    def create_permission(**data) -> Permission:
        data["code"] = PermissionService._validate_permission_code(data["code"])

        PermissionService._validate_unique_name(data["name"])
        PermissionService._validate_unique_code(data["code"])

        permission = Permission(**data)
        permission.full_clean()
        permission.save()

        return permission

    @staticmethod
    def update_permission(permission: Permission, **data) -> Permission:
        if "code" in data:
            data["code"] = PermissionService._validate_permission_code(data["code"])
            PermissionService._validate_unique_code(
                data["code"],
                exclude_id=permission.pk,
            )

        if "name" in data:
            PermissionService._validate_unique_name(
                data["name"],
                exclude_id=permission.pk,
            )

        for field, value in data.items():
            setattr(permission, field, value)

        permission.full_clean()
        permission.save(update_fields=data.keys())

        return permission

    @staticmethod
    def delete_permission(permission: Permission) -> None:
        """
        Delete a permission.
        """
        permission.delete()

    @staticmethod
    def get_permission(permission_id: int) -> Permission:
        """
        Retrieve a permission by ID.
        """
        try:
            return Permission.objects.get(pk=permission_id)
        except Permission.DoesNotExist:
            raise Http404("Permission not found.")

    @staticmethod
    def list_permissions() -> QuerySet[Permission]:
        """
        Retrieve all permissions.
        """
        return Permission.objects.all()