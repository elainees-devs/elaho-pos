from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from rest_framework.test import APITestCase

from apps.roles.models import Role, Permission, RolePermission
from shared.constants import PermissionCode
from shared.permission import HasPermission, HasRoleLevel, IsSuperAdmin

from .factories import RoleFactory, PermissionFactory, RolePermissionFactory, UserFactory


User = get_user_model()


class HasPermissionEnforcementTest(APITestCase):
    def setUp(self):
        self.role = RoleFactory(name="Staff", level=10)
        self.permission = PermissionFactory(code=PermissionCode.ROLE_CREATE.value)
        self.url = "/api/v1/roles/roles/"
        self.payload = {"name": "Test Role", "level": 1}

    def test_unauthenticated_user_gets_403(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, 403)

    def test_user_without_role_gets_403(self):
        user = UserFactory(role=None)
        self.client.force_authenticate(user)
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, 403)

    def test_user_without_permission_gets_403(self):
        user = UserFactory(role=self.role)
        self.client.force_authenticate(user)
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, 403)

    def test_user_with_permission_gets_201(self):
        RolePermissionFactory(role=self.role, permission=self.permission)
        user = UserFactory(role=self.role)
        self.client.force_authenticate(user)
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)


class HasPermissionListViewTest(APITestCase):
    def setUp(self):
        self.role = RoleFactory(name="Viewer", level=1)
        self.permission = PermissionFactory(code=PermissionCode.ROLE_VIEW.value)
        RolePermissionFactory(role=self.role, permission=self.permission)

        # create a role to list
        RoleFactory(name="Target Role", level=5)

    def test_list_with_permission_returns_200(self):
        user = UserFactory(role=self.role)
        self.client.force_authenticate(user)
        response = self.client.get("/api/v1/roles/roles/")
        self.assertEqual(response.status_code, 200)

    def test_list_without_permission_returns_403(self):
        role_no_perm = RoleFactory(name="NoPerm", level=1)
        user = UserFactory(role=role_no_perm)
        self.client.force_authenticate(user)
        response = self.client.get("/api/v1/roles/roles/")
        self.assertEqual(response.status_code, 403)


class IsSuperAdminEnforcementTest(APITestCase):
    def setUp(self):
        self.superadmin_role = Role.objects.create(name="SuperAdmin", level=999)
        self.normal_role = Role.objects.create(name="Manager", level=50)

    def test_superadmin_can_access_role_permission_endpoints(self):
        user = UserFactory(role=self.superadmin_role)
        self.client.force_authenticate(user)

        role = RoleFactory()
        permission = PermissionFactory()
        response = self.client.post(
            "/api/v1/roles/role-permissions/",
            {"role": role.id, "permission": permission.id},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_regular_user_gets_403_on_role_permission_endpoints(self):
        user = UserFactory(role=self.normal_role)
        self.client.force_authenticate(user)

        role = RoleFactory()
        permission = PermissionFactory()
        response = self.client.post(
            "/api/v1/roles/role-permissions/",
            {"role": role.id, "permission": permission.id},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_superadmin_case_insensitive_admin(self):
        from django.test import RequestFactory
        from shared.permission import IsSuperAdmin

        rf = RequestFactory()
        for name in ("superadmin", "SUPERADMIN", "SuperAdmin", "Superadmin"):
            role = Role(name=name, level=999)
            user = get_user_model()(
                email=f"{name.lower()}@example.com",
                first_name="Test",
                last_name="User",
                password="password123",
                role=role,
            )
            request = rf.get("/api/v1/roles/role-permissions/")
            request.user = user
            perm = IsSuperAdmin()
            self.assertTrue(
                perm.has_permission(request, None),
                f"Failed for role name: {name}",
            )

    def test_unauthenticated_user_gets_403(self):
        role = RoleFactory()
        permission = PermissionFactory()
        response = self.client.post(
            "/api/v1/roles/role-permissions/",
            {"role": role.id, "permission": permission.id},
            format="json",
        )
        self.assertEqual(response.status_code, 403)


class HasRoleLevelUnitTest(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.high_level = HasRoleLevel(100)
        self.low_level = HasRoleLevel(10)
        self.mock_view = type("View", (), {})()

    def test_returns_false_for_unauthenticated(self):
        request = self.rf.get("/")
        request.user = type("Anon", (), {"is_authenticated": False})()
        perm = self.high_level()
        self.assertFalse(perm.has_permission(request, self.mock_view))

    def test_returns_false_for_user_without_role(self):
        request = self.rf.get("/")
        user = UserFactory(role=None)
        request.user = user
        perm = self.high_level()
        self.assertFalse(perm.has_permission(request, self.mock_view))

    def test_returns_true_when_level_meets_minimum(self):
        role = RoleFactory(level=50)
        user = UserFactory(role=role)
        request = self.rf.get("/")
        request.user = user

        perm_low = HasRoleLevel(10)()
        self.assertTrue(perm_low.has_permission(request, self.mock_view))

        perm_equal = HasRoleLevel(50)()
        self.assertTrue(perm_equal.has_permission(request, self.mock_view))

    def test_returns_false_when_level_below_minimum(self):
        role = RoleFactory(level=10)
        user = UserFactory(role=role)
        request = self.rf.get("/")
        request.user = user

        perm = HasRoleLevel(50)()
        self.assertFalse(perm.has_permission(request, self.mock_view))
