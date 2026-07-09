from django.test import TestCase

from apps.roles.serializers import (
    RoleSerializer,
    PermissionSerializer,
    RolePermissionSerializer,
)

from apps.roles.models import (
    Role,
    Permission,
    RolePermission,
)


class RoleSerializerTest(TestCase):

    def test_role_serializer(self):

        role = Role.objects.create(
            name="Admin",
            level=100
        )

        serializer = RoleSerializer(role)

        self.assertEqual(
            serializer.data["name"],
            "Admin"
        )


class PermissionSerializerTest(TestCase):

    def test_permission_serializer(self):

        permission = Permission.objects.create(
            name="Delete Product",
            code="products.delete"
        )

        serializer = PermissionSerializer(permission)

        self.assertEqual(
            serializer.data["code"],
            "products.delete"
        )


class RolePermissionSerializerTest(TestCase):

    def test_role_permission_serializer(self):

        role = Role.objects.create(
            name="Cashier"
        )

        permission = Permission.objects.create(
            name="Create Sale",
            code="sales.create"
        )

        assignment = RolePermission.objects.create(
            role=role,
            permission=permission
        )

        serializer = RolePermissionSerializer(
            assignment
        )

        self.assertEqual(
            serializer.data["role"],
            role.id
        )