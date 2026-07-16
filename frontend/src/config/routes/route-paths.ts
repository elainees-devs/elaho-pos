export const ROUTES = {
  // Auth
  VERIFY_EMAIL: "/verify-email",
  FORGOT_PASSWORD: "/forgot-password",
  RESET_PASSWORD: "/reset-password",
  LOGIN: "/login",
  REGISTER: "/register",

  // Dashboard
  DASHBOARD: "/",

  // Sales
  POS: "/pos",
  CUSTOMERS: "/customers",
  CUSTOMER_CREATE: "/customers/create",
  CUSTOMER_EDIT: "/customers/:id/edit",
  SUPPLIERS: "/suppliers",
  SUPPLIER_CREATE: "/suppliers/create",
  SUPPLIER_EDIT: "/suppliers/:id/edit",

  // Inventory
  PRODUCTS: "/products",
  PRODUCT_CREATE: "/products/create",
  PRODUCT_EDIT: "/products/:id/edit",
  CATEGORIES: "/categories",
  INVENTORY: "/inventory",
  PURCHASES: "/purchases",
  PURCHASE_CREATE: "/purchases/create",
  PURCHASE_EDIT: "/purchases/:id/edit",

  // Finance
  EXPENSES: "/expenses",
  EXPENSE_CREATE: "/expenses/create",
  EXPENSE_EDIT: "/expenses/:id/edit",
  REPORTS: "/reports",

  // Administration
  USERS: "/users",
  USER_CREATE: "/users/create",
  USER_EDIT: "/users/:id/edit",
  ROLES: "/roles",
  ROLE_CREATE: "/roles/create",
  ROLE_EDIT: "/roles/:id/edit",
  PERMISSIONS: "/permissions",

  // System
  NOTIFICATIONS: "/notifications",
  SETTINGS: "/settings",
} as const
