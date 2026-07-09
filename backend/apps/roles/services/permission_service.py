from django.db import transaction
from django.db.models import QuerySet
from django.core.exceptions import ValidationError

from ..models import Permission, Role


class PermissionService:
    """
    Service responsible for permission management.

    Responsibilities:
    - Create permission
    - Update permissions
    - Delete permissions
    - Assign permissions to roles
    - Retrieve permissions
    """
    @staticmethod
    def create_permission(**data) -> Permission:
        """
        Create a new permission.
        """
        if Permission.objects.filter(name=data["name"]).exists():
            raise ValidationError("Permission already exists.")
        return Permission.objects.create(**data)
    

    @staticmethod
    def update_permission(permission: Permission, **data) -> Permission:
        new_name = data.get("name")

        if (
        new_name
        and Permission.objects.exclude(pk=permission.pk)
        .filter(name=new_name)
        .exists()
    ):
            raise ValidationError("Permission already exists.")

        for field, value in data.items():
            setattr(permission, field, value)

        permission.full_clean()
        permission.save()

        return permission

    @staticmethod
    def delete_permission(permission:Permission) -> None:
        """
        Delete a permission.
        """
        permission.delete()

    @staticmethod
    @transaction.atomic
    def assign_permission(role: Role, permission: Permission) -> Role:
        role.permission = permission
        role.save(update_fields=["permission"])
        return role
    
    @staticmethod
    def get_permission(permission_id: int) -> Permission:
        try:
            return Permission.objects.get(pk=permission_id)
        except Permission.DoesNotExist:
            raise ValidationError("Permission not found.")

    @staticmethod
    def list_permissions() -> QuerySet[Permission]:
        return Permission.objects.all()