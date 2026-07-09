from django.core.exceptions import ValidationError
from django.db.models import QuerySet

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
    def create_permission(**data) -> Permission:
        """
        Create a new permission.
        """
        PermissionService._validate_unique_name(data["name"])
        return Permission.objects.create(**data)

    @staticmethod
    def update_permission(permission: Permission, **data) -> Permission:
        """
        Update an existing permission.
        """
        new_name = data.get("name")

        if new_name:
            PermissionService._validate_unique_name(
                new_name,
                exclude_id=permission.pk,
            )

        for field, value in data.items():
            setattr(permission, field, value)

        permission.full_clean()
        permission.save()

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
            raise ValidationError("Permission not found.")

    @staticmethod
    def list_permissions() -> QuerySet[Permission]:
        """
        Retrieve all permissions.
        """
        return Permission.objects.all()