from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet

from ..models import Permission, Role, RolePermission


class RolePermissionService:
    """
    Service responsible for role-permission management.

    Responsibilities:
    - Assign permissions to roles
    - Update role-permission mappings
    - Remove permissions from roles
    - Retrieve role-permission mappings
    """

    @staticmethod
    def assign_permission(role: Role, permission: Permission) -> RolePermission:
        """
        Assign a permission to a role.
        """
        if RolePermission.objects.filter(
            role=role,
            permission=permission,
        ).exists():
            raise ValidationError(
                "Permission is already assigned to this role."
            )

        return RolePermission.objects.create(
            role=role,
            permission=permission,
        )

    @staticmethod
    def update_role_permission(
        role_permission: RolePermission,
        **data,
    ) -> RolePermission:
        """
        Update an existing role-permission mapping.
        """

        role = data.get("role", role_permission.role)
        permission = data.get("permission", role_permission.permission)

        if (
            RolePermission.objects.exclude(pk=role_permission.pk)
            .filter(
                role=role,
                permission=permission,
            )
            .exists()
        ):
            raise ValidationError(
                "Permission is already assigned to this role."
            )

        for field, value in data.items():
            setattr(role_permission, field, value)

        role_permission.full_clean()
        role_permission.save()

        return role_permission

    @staticmethod
    def remove_permission(role_permission: RolePermission) -> None:
        """
        Remove a permission from a role.
        """
        role_permission.delete()

    @staticmethod
    @transaction.atomic
    def replace_permissions(
        role: Role,
        permissions: list[Permission],
    ) -> None:
        """
        Replace all permissions assigned to a role.
        """

        RolePermission.objects.filter(role=role).delete()

        RolePermission.objects.bulk_create(
            [
                RolePermission(
                    role=role,
                    permission=permission,
                )
                for permission in permissions
            ]
        )

    @staticmethod
    def get_role_permission(
        role_permission_id: int,
    ) -> RolePermission:
        """
        Retrieve a role-permission mapping by ID.
        """
        try:
            return RolePermission.objects.get(pk=role_permission_id)
        except RolePermission.DoesNotExist:
            raise ValidationError(
                "Role permission mapping not found."
            )

    @staticmethod
    def list_role_permissions() -> QuerySet[RolePermission]:
        """
        Retrieve all role-permission mappings.
        """
        return RolePermission.objects.select_related(
            "role",
            "permission",
        ).all()

    @staticmethod
    def list_permissions_by_role(
        role: Role,
    ) -> QuerySet[RolePermission]:
        """
        Retrieve all permissions assigned to a role.
        """
        return RolePermission.objects.filter(role=role).select_related(
            "permission"
        )

    @staticmethod
    def list_roles_by_permission(
        permission: Permission,
    ) -> QuerySet[RolePermission]:
        """
        Retrieve all roles assigned to a permission.
        """
        return RolePermission.objects.filter(
            permission=permission
        ).select_related("role")

    @staticmethod
    def has_permission(
        role: Role,
        permission: Permission,
    ) -> bool:
        """
        Check whether a role has a specific permission.
        """
        return RolePermission.objects.filter(
            role=role,
            permission=permission,
        ).exists()