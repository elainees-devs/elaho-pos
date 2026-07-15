from django.core.management.base import BaseCommand

from apps.roles.models import Permission, Role, RolePermission
from shared.constants import PermissionCode


# Role definitions: (name, level, description)
DEFAULT_ROLES = [
    ("Admin", 100, "Full system control. Can manage all users, roles, and settings."),
    ("Manager", 50, "Shop operations manager. Can manage users, inventory, and view reports."),
    ("Staff", 10, "Frontline staff. Can process sales and view products."),
]

# Permission assignments by role name.
# Admin gets everything. Manager gets user + operational perms. Staff gets minimal.
ROLE_PERMISSIONS = {
    "Admin": [
        # User management
        PermissionCode.USER_CREATE,
        PermissionCode.USER_VIEW,
        PermissionCode.USER_UPDATE,
        PermissionCode.USER_DELETE,
        # Role management
        PermissionCode.ROLE_CREATE,
        PermissionCode.ROLE_VIEW,
        PermissionCode.ROLE_UPDATE,
        PermissionCode.ROLE_DELETE,
        # Permission management
        PermissionCode.PERMISSION_CREATE,
        PermissionCode.PERMISSION_VIEW,
        PermissionCode.PERMISSION_UPDATE,
        PermissionCode.PERMISSION_DELETE,
        # Dashboard
        PermissionCode.DASHBOARD_VIEW,
        # Reports
        PermissionCode.REPORT_VIEW,
        PermissionCode.REPORT_EXPORT,
        # Inventory
        PermissionCode.INVENTORY_CREATE,
        PermissionCode.INVENTORY_VIEW,
        PermissionCode.INVENTORY_UPDATE,
        PermissionCode.INVENTORY_DELETE,
        # Sales
        PermissionCode.SALE_CREATE,
        PermissionCode.SALE_VIEW,
        PermissionCode.SALE_UPDATE,
        PermissionCode.SALE_DELETE,
        # Customers
        PermissionCode.CUSTOMER_CREATE,
        PermissionCode.CUSTOMER_VIEW,
        PermissionCode.CUSTOMER_UPDATE,
        PermissionCode.CUSTOMER_DELETE,
        # Suppliers
        PermissionCode.SUPPLIER_CREATE,
        PermissionCode.SUPPLIER_VIEW,
        PermissionCode.SUPPLIER_UPDATE,
        PermissionCode.SUPPLIER_DELETE,
    ],
    "Manager": [
        # User management (can create and manage staff)
        PermissionCode.USER_CREATE,
        PermissionCode.USER_VIEW,
        PermissionCode.USER_UPDATE,
        PermissionCode.USER_DELETE,
        # Dashboard
        PermissionCode.DASHBOARD_VIEW,
        # Reports
        PermissionCode.REPORT_VIEW,
        PermissionCode.REPORT_EXPORT,
        # Inventory
        PermissionCode.INVENTORY_CREATE,
        PermissionCode.INVENTORY_VIEW,
        PermissionCode.INVENTORY_UPDATE,
        PermissionCode.INVENTORY_DELETE,
        # Sales
        PermissionCode.SALE_CREATE,
        PermissionCode.SALE_VIEW,
        PermissionCode.SALE_UPDATE,
        PermissionCode.SALE_DELETE,
        # Customers
        PermissionCode.CUSTOMER_CREATE,
        PermissionCode.CUSTOMER_VIEW,
        PermissionCode.CUSTOMER_UPDATE,
        PermissionCode.CUSTOMER_DELETE,
        # Suppliers
        PermissionCode.SUPPLIER_CREATE,
        PermissionCode.SUPPLIER_VIEW,
        PermissionCode.SUPPLIER_UPDATE,
        PermissionCode.SUPPLIER_DELETE,
    ],
    "Staff": [
        # Dashboard
        PermissionCode.DASHBOARD_VIEW,
        # Sales (can create and view sales)
        PermissionCode.SALE_CREATE,
        PermissionCode.SALE_VIEW,
        # Customers (can view customers)
        PermissionCode.CUSTOMER_VIEW,
        # Inventory (read-only)
        PermissionCode.INVENTORY_VIEW,
    ],
}


class Command(BaseCommand):
    help = "Seed the database with default roles and permissions."

    def handle(self, *args, **options):
        self.stdout.write("Seeding roles and permissions...")

        # Create permissions from PermissionCode enum.
        created_perms = 0
        for perm_code in PermissionCode:
            _, created = Permission.objects.get_or_create(
                code=perm_code.value,
                defaults={
                    "name": perm_code.value.replace(".", " ").title(),
                    "description": f"Permission: {perm_code.value}",
                },
            )
            if created:
                created_perms += 1
        self.stdout.write(f"  Permissions: {created_perms} created")

        # Create roles and assign permissions.
        for name, level, description in DEFAULT_ROLES:
            role, created = Role.objects.get_or_create(
                name=name,
                defaults={"level": level, "description": description},
            )
            if created:
                self.stdout.write(f"  Role '{name}' created (level {level})")
            else:
                self.stdout.write(f"  Role '{name}' already exists")

            # Assign permissions to role.
            perm_codes = ROLE_PERMISSIONS.get(name, [])
            assigned = 0
            for perm_code in perm_codes:
                perm, _ = Permission.objects.get_or_create(
                    code=perm_code.value,
                    defaults={
                        "name": perm_code.value.replace(".", " ").title(),
                        "description": f"Permission: {perm_code.value}",
                    },
                )
                _, created = RolePermission.objects.get_or_create(
                    role=role,
                    permission=perm,
                )
                if created:
                    assigned += 1
            self.stdout.write(f"  Assigned {assigned} permissions to '{name}'")

        self.stdout.write(self.style.SUCCESS("Done."))
