from django.core.exceptions import ValidationError
from django.http import Http404
from django.test import TestCase

from shared.constants import PermissionCode

from ..models import Permission, Role, RolePermission
from ..services.permission_service import PermissionService
from ..services.role_permission_service import RolePermissionService


class PermissionServiceCreateTest(TestCase):
    def test_create_with_valid_canonical_code(self):
        permission = PermissionService.create_permission(
            name="Create User",
            code=PermissionCode.USER_CREATE,
        )
        self.assertEqual(permission.code, "user.create")
        self.assertEqual(permission.name, "Create User")

    def test_create_with_valid_code_string(self):
        permission = PermissionService.create_permission(
            name="View Role",
            code="role.view",
        )
        self.assertEqual(permission.code, "role.view")

    def test_create_with_invalid_code_raises(self):
        with self.assertRaises(ValidationError):
            PermissionService.create_permission(
                name="Bad",
                code="not.a.valid.code",
            )

    def test_create_duplicate_name_raises(self):
        PermissionService.create_permission(
            name="Unique Name",
            code=PermissionCode.USER_CREATE,
        )
        with self.assertRaises(ValidationError):
            PermissionService.create_permission(
                name="Unique Name",
                code=PermissionCode.ROLE_CREATE,
            )

    def test_create_duplicate_code_raises(self):
        PermissionService.create_permission(
            name="First",
            code=PermissionCode.USER_CREATE,
        )
        with self.assertRaises(ValidationError):
            PermissionService.create_permission(
                name="Second",
                code=PermissionCode.USER_CREATE,
            )


class PermissionServiceUpdateTest(TestCase):
    def setUp(self):
        self.permission = PermissionService.create_permission(
            name="Original",
            code=PermissionCode.USER_CREATE,
        )

    def test_update_name(self):
        updated = PermissionService.update_permission(
            self.permission,
            name="Renamed",
        )
        self.assertEqual(updated.name, "Renamed")

    def test_update_code_to_valid_value(self):
        updated = PermissionService.update_permission(
            self.permission,
            code=PermissionCode.USER_VIEW,
        )
        self.assertEqual(updated.code, "user.view")

    def test_update_code_to_invalid_value_raises(self):
        with self.assertRaises(ValidationError):
            PermissionService.update_permission(
                self.permission,
                code="invalid.code",
            )

    def test_update_name_to_duplicate_raises(self):
        PermissionService.create_permission(
            name="Existing",
            code=PermissionCode.ROLE_CREATE,
        )
        with self.assertRaises(ValidationError):
            PermissionService.update_permission(
                self.permission,
                name="Existing",
            )

    def test_update_code_to_duplicate_raises(self):
        PermissionService.create_permission(
            name="Other",
            code=PermissionCode.ROLE_CREATE,
        )
        with self.assertRaises(ValidationError):
            PermissionService.update_permission(
                self.permission,
                code=PermissionCode.ROLE_CREATE,
            )

    def test_update_same_name_succeeds(self):
        updated = PermissionService.update_permission(
            self.permission,
            name="Original",
        )
        self.assertEqual(updated.name, "Original")


class PermissionServiceDeleteTest(TestCase):
    def setUp(self):
        self.permission = PermissionService.create_permission(
            name="To Delete",
            code=PermissionCode.USER_DELETE,
        )

    def test_delete_removes_from_database(self):
        pk = self.permission.pk
        PermissionService.delete_permission(self.permission)
        self.assertFalse(Permission.objects.filter(pk=pk).exists())


class PermissionServiceGetTest(TestCase):
    def setUp(self):
        self.permission = PermissionService.create_permission(
            name="Get Me",
            code=PermissionCode.USER_VIEW,
        )

    def test_get_existing_returns_instance(self):
        result = PermissionService.get_permission(self.permission.pk)
        self.assertEqual(result.pk, self.permission.pk)

    def test_get_non_existing_raises_http404(self):
        with self.assertRaises(Http404):
            PermissionService.get_permission(99999)


class PermissionServiceListTest(TestCase):
    def test_list_returns_all_permissions(self):
        PermissionService.create_permission(
            name="Alpha",
            code=PermissionCode.USER_CREATE,
        )
        PermissionService.create_permission(
            name="Beta",
            code=PermissionCode.ROLE_CREATE,
        )
        results = PermissionService.list_permissions()
        self.assertEqual(results.count(), 2)


class RolePermissionServiceAssignTest(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Manager", level=50)
        self.permission = Permission.objects.create(
            name="View Users",
            code="user.view",
        )

    def test_assign_new_creates_mapping(self):
        rp = RolePermissionService.assign_permission(
            self.role,
            self.permission,
        )
        self.assertEqual(rp.role, self.role)
        self.assertEqual(rp.permission, self.permission)

    def test_assign_duplicate_raises(self):
        RolePermissionService.assign_permission(
            self.role,
            self.permission,
        )
        with self.assertRaises(ValidationError):
            RolePermissionService.assign_permission(
                self.role,
                self.permission,
            )


class RolePermissionServiceUpdateTest(TestCase):
    def setUp(self):
        self.role_a = Role.objects.create(name="Admin", level=999)
        self.role_b = Role.objects.create(name="Staff", level=10)
        self.perm_view = Permission.objects.create(
            name="View",
            code="role.view",
        )
        self.perm_create = Permission.objects.create(
            name="Create",
            code="role.create",
        )
        self.rp = RolePermissionService.assign_permission(
            self.role_a,
            self.perm_view,
        )

    def test_update_changes_role(self):
        updated = RolePermissionService.update_role_permission(
            self.rp,
            role=self.role_b,
        )
        self.assertEqual(updated.role, self.role_b)

    def test_update_changes_permission(self):
        updated = RolePermissionService.update_role_permission(
            self.rp,
            permission=self.perm_create,
        )
        self.assertEqual(updated.permission, self.perm_create)

    def test_update_to_duplicate_raises(self):
        RolePermissionService.assign_permission(
            self.role_a,
            self.perm_create,
        )
        with self.assertRaises(ValidationError):
            RolePermissionService.update_role_permission(
                self.rp,
                permission=self.perm_create,
            )


class RolePermissionServiceRemoveTest(TestCase):
    def setUp(self):
        role = Role.objects.create(name="Temp", level=1)
        perm = Permission.objects.create(name="Temp", code="temp.perm")
        self.rp = RolePermissionService.assign_permission(role, perm)

    def test_remove_deletes_mapping(self):
        pk = self.rp.pk
        RolePermissionService.remove_permission(self.rp)
        self.assertFalse(
            RolePermission.objects.filter(pk=pk).exists()
        )


class RolePermissionServiceReplaceTest(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Manager", level=50)
        self.perm_a = Permission.objects.create(
            name="A",
            code="perm.a",
        )
        self.perm_b = Permission.objects.create(
            name="B",
            code="perm.b",
        )
        self.perm_c = Permission.objects.create(
            name="C",
            code="perm.c",
        )

    def test_replace_swaps_all_permissions(self):
        RolePermissionService.assign_permission(self.role, self.perm_a)
        RolePermissionService.assign_permission(self.role, self.perm_b)

        RolePermissionService.replace_permissions(
            self.role,
            [self.perm_c],
        )

        remaining = list(
            RolePermissionService.list_permissions_by_role(self.role)
        )
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].permission, self.perm_c)


class RolePermissionServiceGetTest(TestCase):
    def setUp(self):
        role = Role.objects.create(name="Viewer", level=5)
        perm = Permission.objects.create(
            name="View",
            code="report.view",
        )
        self.rp = RolePermissionService.assign_permission(role, perm)

    def test_get_existing_returns_mapping(self):
        result = RolePermissionService.get_role_permission(self.rp.pk)
        self.assertEqual(result.pk, self.rp.pk)

    def test_get_non_existing_raises(self):
        with self.assertRaises(ValidationError):
            RolePermissionService.get_role_permission(99999)


class RolePermissionServiceListTest(TestCase):
    def setUp(self):
        role = Role.objects.create(name="Admin", level=999)
        perm_a = Permission.objects.create(
            name="Alpha",
            code="alpha.perm",
        )
        perm_b = Permission.objects.create(
            name="Beta",
            code="beta.perm",
        )
        RolePermissionService.assign_permission(role, perm_a)
        RolePermissionService.assign_permission(role, perm_b)

    def test_list_all_returns_all(self):
        results = RolePermissionService.list_role_permissions()
        self.assertEqual(results.count(), 2)

    def test_list_by_role_filters_correctly(self):
        role_b = Role.objects.create(name="Other", level=1)
        perm = Permission.objects.create(
            name="Extra",
            code="extra.perm",
        )
        RolePermissionService.assign_permission(role_b, perm)

        results = RolePermissionService.list_permissions_by_role(role_b)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results[0].permission.code, "extra.perm")

    def test_list_by_permission_filters_correctly(self):
        perm_alpha = Permission.objects.get(code="alpha.perm")
        results = RolePermissionService.list_roles_by_permission(
            perm_alpha,
        )
        self.assertEqual(results.count(), 1)
        self.assertEqual(results[0].role.name, "Admin")


class RolePermissionServiceHasPermissionTest(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name="Staff", level=10)
        self.perm = Permission.objects.create(
            name="View Dashboard",
            code="dashboard.view",
        )
        RolePermissionService.assign_permission(self.role, self.perm)

    def test_has_permission_true_when_assigned(self):
        self.assertTrue(
            RolePermissionService.has_permission(self.role, self.perm)
        )

    def test_has_permission_false_when_not_assigned(self):
        other_perm = Permission.objects.create(
            name="Other",
            code="other.perm",
        )
        self.assertFalse(
            RolePermissionService.has_permission(self.role, other_perm)
        )
