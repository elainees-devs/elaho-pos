from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.roles.models import (
    Role,
    Permission,
    RolePermission,
)
from shared.constants import PermissionCode

from .factories import RoleFactory, PermissionFactory


User = get_user_model()


class AuthenticatedAPITestCase(APITestCase):
    """
    Base test class that creates an authenticated superuser
    for API requests.
    """

    def setUp(self):
        self.role = RoleFactory(name="SuperAdmin", level=999)
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            role=self.role,
            is_superuser=True,
        )

        self.client.force_authenticate(
            user=self.user
        )


class RoleViewSetTest(AuthenticatedAPITestCase):

    def setUp(self):
        super().setUp()
        perm = PermissionFactory(code=PermissionCode.ROLE_CREATE.value)
        RolePermission.objects.create(role=self.role, permission=perm)

    def test_create_role(self):

        response = self.client.post(
            "/api/v1/roles/",
            {
                "name": "Manager",
                "level": 50,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )


class PermissionViewSetTest(AuthenticatedAPITestCase):

    def setUp(self):
        super().setUp()
        perm = PermissionFactory(code=PermissionCode.PERMISSION_CREATE.value)
        RolePermission.objects.create(role=self.role, permission=perm)

    def test_create_permission(self):

        response = self.client.post(
            "/api/v1/roles/permissions/",
            {
                "name": "View Reports",
                "code": "report.view",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )


class RolePermissionViewSetTest(AuthenticatedAPITestCase):

    def setUp(self):
        super().setUp()

    def test_create_role_permission(self):

        role = Role.objects.create(
            name="Admin",
            level=100,
        )

        permission = Permission.objects.create(
            name="Delete User",
            code="users.delete",
        )

        response = self.client.post(
            "/api/v1/roles/role-permissions/",
            {
                "role": role.id,
                "permission": permission.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )