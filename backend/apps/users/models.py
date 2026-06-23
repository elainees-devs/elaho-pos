from django.db import models


class User:

    # 1. Define user base class properties
    # - email (read-only or validated property)
    # - role (controlled via getter/setter)
    # - is_active (boolean property with validation)
    # - derived properties like is_staff, is_owner, is_superadmin
    pass


class SuperAdmin:

    # 2. Define super admin class
    # - inherits from User
    # - overrides or extends permissions behavior
    # - always returns full access flags (all permissions = True)
    # - may include extra properties like system-level access rights
    pass


class Manager:

    # 3. Define manager class
    # - inherits from User
    # - handles business-level operations (store management logic)
    # - can approve/override staff actions (e.g. refunds, discounts)
    # - has limited admin permissions (not full system control)
    # - can access reports, inventory management, and sales summaries
    # - cannot modify system-level settings or superadmin privileges
    pass


class Staff:

    # 4. Define staff class
    # - inherits from User
    # - handles daily operational tasks (sales, customer service)
    # - can create sales transactions but with restricted permissions
    # - cannot approve refunds or modify inventory levels
    # - cannot access financial reports or admin settings
    # - works under manager supervision
    pass