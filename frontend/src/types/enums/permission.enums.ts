export enum PermissionCode {
    // User permissions
    USER_CREATE = "user.create",
    USER_VIEW = "user.view",
    USER_UPDATE = "user.update",
    USER_DELETE = "user.delete",

    // Role permissions
    ROLE_CREATE = "role.create",
    ROLE_VIEW = "role.view",
    ROLE_UPDATE = "role.update",
    ROLE_DELETE = "role.delete",

    // Permission permissions
    PERMISSION_CREATE = "permission.create",
    PERMISSION_VIEW = "permission.view",
    PERMISSION_UPDATE = "permission.update",
    PERMISSION_DELETE = "permission.delete",

    // Dashboard
    DASHBOARD_VIEW = "dashboard.view",

    // Reports
    REPORT_VIEW = "report.view",
    REPORT_EXPORT = "report.export",

    // Inventory
    INVENTORY_CREATE = "inventory.create",
    INVENTORY_VIEW = "inventory.view",
    INVENTORY_UPDATE = "inventory.update",
    INVENTORY_DELETE = "inventory.delete",

    // Sales
    SALE_CREATE = "sale.create",
    SALE_VIEW = "sale.view",
    SALE_UPDATE = "sale.update",
    SALE_DELETE = "sale.delete",

    // Customers
    CUSTOMER_CREATE = "customer.create",
    CUSTOMER_VIEW = "customer.view",
    CUSTOMER_UPDATE = "customer.update",
    CUSTOMER_DELETE = "customer.delete",

    //  Suppliers
    SUPPLIER_CREATE = "supplier.create",
    SUPPLIER_VIEW = "supplier.view",
    SUPPLIER_UPDATE = "supplier.update",
    SUPPLIER_DELETE = "supplier.delete",


    PERM_CACHE_PREFIX = "perm_codes_", //  Prefix used for caching user permission codes.

    PERM_CACHE_TTL = 300 // Cache expiration time in seconds (300 = 5 minutes)
}