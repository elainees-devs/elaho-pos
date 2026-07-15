from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from apps.roles.models import Role, Permission, RolePermission
from shared.constants import PermissionCode
from apps.roles.tests.factories import RoleFactory, PermissionFactory


User = get_user_model()


class UserViewSetTest(APITestCase):
    """
    Tests for UserViewSet CRUD operations.
    """

    def setUp(self):
        self.role = RoleFactory(name="SuperAdmin", level=999)
        self.user = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            first_name="Admin",
            last_name="User",
            role=self.role,
        )

        for perm_code in [
            PermissionCode.USER_CREATE,
            PermissionCode.USER_VIEW,
            PermissionCode.USER_UPDATE,
            PermissionCode.USER_DELETE,
        ]:
            perm = PermissionFactory(code=perm_code.value)
            RolePermission.objects.create(role=self.role, permission=perm)

        self.client.force_authenticate(
            user=self.user
        )


    def test_create_user(self):

        response = self.client.post(
            "/api/v1/users/",
            {
                "email": "newuser@example.com",
                "password": "password123",
                "first_name": "New",
                "last_name": "User",
                "phone": "0711111111",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            response.data["email"],
            "newuser@example.com",
        )

        self.assertEqual(
            response.data["first_name"],
            "New",
        )


    def test_list_users(self):

        User.objects.create_user(
            email="second@example.com",
            password="password123",
            first_name="Second",
            last_name="User",
        )

        response = self.client.get(
            "/api/v1/users/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertGreaterEqual(
            len(response.data),
            2,
        )


    def test_retrieve_user(self):

        user = User.objects.create_user(
            email="retrieve@example.com",
            password="password123",
            first_name="Retrieve",
            last_name="User",
        )

        response = self.client.get(
            f"/api/v1/users/{user.id}/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["email"],
            "retrieve@example.com",
        )


    def test_update_user(self):

        user = User.objects.create_user(
            email="update@example.com",
            password="password123",
            first_name="Old",
            last_name="Name",
        )

        response = self.client.patch(
            f"/api/v1/users/{user.id}/",
            {
                "first_name": "Updated",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["first_name"],
            "Updated",
        )


    def test_delete_user(self):

        user = User.objects.create_user(
            email="delete@example.com",
            password="password123",
            first_name="Delete",
            last_name="User",
        )

        response = self.client.delete(
            f"/api/v1/users/{user.id}/",
        )

        self.assertEqual(
            response.status_code,
            204,
        )


class ManagerUserCreateTest(APITestCase):
    """
    Tests that Manager/Business Owner role can create users.
    """

    def setUp(self):
        self.manager_role = RoleFactory(name="Manager", level=50)
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="password123",
            first_name="Manager",
            last_name="User",
            role=self.manager_role,
        )

        for perm_code in [
            PermissionCode.USER_CREATE,
            PermissionCode.USER_VIEW,
            PermissionCode.USER_UPDATE,
            PermissionCode.USER_DELETE,
        ]:
            perm = PermissionFactory(code=perm_code.value)
            RolePermission.objects.create(role=self.manager_role, permission=perm)

        self.client.force_authenticate(user=self.manager)

    def test_manager_can_create_user(self):
        response = self.client.post(
            "/api/v1/users/",
            {
                "email": "staff@example.com",
                "password": "password123",
                "first_name": "Staff",
                "last_name": "User",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["email"], "staff@example.com")

    def test_manager_can_list_users(self):
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, 200)

    def test_manager_can_update_user(self):
        user = User.objects.create_user(
            email="target@example.com",
            password="password123",
            first_name="Target",
            last_name="User",
        )
        response = self.client.patch(
            f"/api/v1/users/{user.id}/",
            {"first_name": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "Updated")

    def test_manager_can_delete_user(self):
        user = User.objects.create_user(
            email="todelete@example.com",
            password="password123",
            first_name="Delete",
            last_name="User",
        )
        response = self.client.delete(f"/api/v1/users/{user.id}/")
        self.assertEqual(response.status_code, 204)


class StaffCannotCreateUserTest(APITestCase):
    """
    Tests that Staff role (without user.create) cannot create users.
    """

    def setUp(self):
        self.staff_role = RoleFactory(name="Staff", level=10)
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="password123",
            first_name="Staff",
            last_name="User",
            role=self.staff_role,
        )
        # Staff only gets sales-related permissions, not user.create
        perm = PermissionFactory(code=PermissionCode.SALE_CREATE.value)
        RolePermission.objects.create(role=self.staff_role, permission=perm)

        self.client.force_authenticate(user=self.staff)

    def test_staff_cannot_create_user(self):
        response = self.client.post(
            "/api/v1/users/",
            {
                "email": "newuser@example.com",
                "password": "password123",
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_staff_can_list_users_if_permitted(self):
        # Staff without user.view also gets 403
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, 403)