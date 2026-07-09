from django.test import TestCase

from apps.roles.models import (
    Role,
    Permission,
    RolePermission,
)


class RoleModelTest(TestCase):

    def test_create_role(self):
        role = Role.objects.create(
            name="Manager",
            description="Store manager role",
            level=50,
        )

        self.assertEqual(role.name, "Manager")
        self.assertEqual(role.level, 50)


class PermissionModelTest(TestCase):

    def test_create_permission(self):
        permission = Permission.objects.create(
            name="Create Product",
            code="products.create",
            description="Allows product creation",
        )

        self.assertEqual(
            permission.code,
            "products.create"
        )


class RolePermissionModelTest(TestCase):

    def test_assign_permission_to_role(self):

        role = Role.objects.create(
            name="Manager"
        )

        permission = Permission.objects.create(
            name="View Reports",
            code="reports.view"
        )

        role_permission = RolePermission.objects.create(
            role=role,
            permission=permission
        )

        self.assertEqual(
            role_permission.role,
            role
        )

        self.assertEqual(
            role_permission.permission,
            permission
        )