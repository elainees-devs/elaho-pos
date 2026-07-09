from rest_framework.test import APITestCase

from shared.constants import PermissionCode

from .factories import RoleFactory, PermissionFactory, RolePermissionFactory, UserFactory


class FullAuthFlowIntegrationTest(APITestCase):
    def setUp(self):
        self.admin_role = RoleFactory(name="SuperAdmin", level=999)
        self.manager_role = RoleFactory(name="Manager", level=50)
        self.staff_role = RoleFactory(name="Staff", level=10)

        self.view_perm = PermissionFactory(code=PermissionCode.ROLE_VIEW.value)
        self.create_perm = PermissionFactory(code=PermissionCode.ROLE_CREATE.value)
        self.update_perm = PermissionFactory(code=PermissionCode.ROLE_UPDATE.value)

        RolePermissionFactory(role=self.admin_role, permission=self.view_perm)
        RolePermissionFactory(role=self.admin_role, permission=self.create_perm)
        RolePermissionFactory(role=self.admin_role, permission=self.update_perm)
        RolePermissionFactory(role=self.manager_role, permission=self.view_perm)

    def test_full_auth_scenario_role_crud(self):
        admin_user = UserFactory(role=self.admin_role)
        self.client.force_authenticate(admin_user)

        response = self.client.post(
            "/api/v1/roles/roles/",
            {"name": "New Role", "level": 20},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        new_role_id = response.data["id"]

        response = self.client.get("/api/v1/roles/roles/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f"/api/v1/roles/roles/{new_role_id}/")
        self.assertEqual(response.status_code, 200)

        response = self.client.patch(
            f"/api/v1/roles/roles/{new_role_id}/",
            {"level": 25},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["level"], 25)

    def test_role_level_enforcement(self):
        manager_user = UserFactory(role=self.manager_role)
        admin_user = UserFactory(role=self.admin_role)

        # Admin (level 999) should pass
        self.client.force_authenticate(admin_user)
        admin_role = RoleFactory()
        admin_perm = PermissionFactory()
        response = self.client.post(
            "/api/v1/roles/role-permissions/",
            {"role": admin_role.id, "permission": admin_perm.id},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        # Manager (level 50) should be denied
        self.client.force_authenticate(manager_user)
        response = self.client.post(
            "/api/v1/roles/role-permissions/",
            {"role": admin_role.id, "permission": admin_perm.id},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_permission_granting_and_revocation(self):
        staff_user = UserFactory(role=self.staff_role)
        self.client.force_authenticate(staff_user)

        # Staff has no permissions, should be denied
        response = self.client.get("/api/v1/roles/roles/")
        self.assertEqual(response.status_code, 403)

        # Grant view permission to staff
        RolePermissionFactory(role=self.staff_role, permission=self.view_perm)

        # Now staff should be able to list roles
        response = self.client.get("/api/v1/roles/roles/")
        self.assertEqual(response.status_code, 200)

        # But still can't create
        response = self.client.post(
            "/api/v1/roles/roles/",
            {"name": "Unauthorized", "level": 99},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_access_denied(self):
        response = self.client.get("/api/v1/roles/roles/")
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            "/api/v1/roles/roles/",
            {"name": "Hacker", "level": 999},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_superadmin_isolation(self):
        regular_user = UserFactory(role=self.manager_role)

        # Regular user cannot access role-permission endpoints
        self.client.force_authenticate(regular_user)
        response = self.client.get("/api/v1/roles/role-permissions/")
        self.assertEqual(response.status_code, 403)

        # Superadmin can access role-permission endpoints
        admin_user = UserFactory(role=self.admin_role)
        self.client.force_authenticate(admin_user)
        response = self.client.get("/api/v1/roles/role-permissions/")
        self.assertEqual(response.status_code, 200)

    def test_cross_resource_permission_isolation(self):
        user_perm = PermissionFactory(code=PermissionCode.USER_CREATE.value)
        RolePermissionFactory(role=self.staff_role, permission=user_perm)

        staff_user = UserFactory(role=self.staff_role)
        self.client.force_authenticate(staff_user)

        # Staff has USER_CREATE but not ROLE_CREATE
        response = self.client.post(
            "/api/v1/roles/roles/",
            {"name": "Should Fail", "level": 1},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

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
        self.assertEqual(response.status_code, 201)
