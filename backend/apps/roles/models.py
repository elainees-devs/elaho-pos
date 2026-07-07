from django.db import models


class Role(models.Model):
    """
    CORE IDEA (SOLID DESIGN):

    This class represents ONLY a user role.

    A role is simply a category assigned to a user.

    Examples:
    - SuperAdmin
    - Manager
    - Staff

    It MUST NOT contain:
    - permission logic
    - authentication logic
    - authorization rules
    - business logic
    - sales logic
    - inventory logic

    Those responsibilities belong to:
    - Permission models
    - Authorization services
    - Business services
    """

    # -----------------------------
    # 1. ROLE IDENTITY (SRP)
    # -----------------------------

    # name:
    # - unique role name
    # - identifies the role within the system
    #
    # Examples:
    # - SuperAdmin
    # - Manager
    # - Staff

    # -----------------------------
    # 2. ROLE DESCRIPTION
    # -----------------------------

    # description:
    # - explains the purpose of the role
    # - documentation only
    # - should NEVER be used for authorization

    # -----------------------------
    # 3. HIERARCHY LEVEL
    # -----------------------------

    # level:
    # - optional ranking of roles
    # - useful for ordering and display
    #
    # Example:
    # 100 = SuperAdmin
    #  50 = Manager
    #  10 = Staff
    #
    # IMPORTANT:
    # This is NOT a permission system.
    # Permissions must be resolved separately.

    # -----------------------------
    # 4. ROLE STATUS
    # -----------------------------

    # is_active:
    # - determines whether the role can be assigned
    # - allows disabling a role without deleting it

    # -----------------------------
    # 5. SYSTEM METADATA
    # -----------------------------

    # created_at:
    # - records when the role was created

    # updated_at:
    # - records the last modification

    # -----------------------------
    # 6. RELATIONSHIPS (NOT OWNED LOGIC)
    # -----------------------------

    # users:
    # - users are assigned to one role
    # - role should not manage user behavior

    # permissions:
    # - permissions are linked externally
    # - role only groups permissions
    # - permission evaluation belongs to the authorization layer

    # -----------------------------
    # 7. DERIVED CONCEPTS
    # -----------------------------

    # A role itself does NOT answer:
    #
    # - Can create sales?
    # - Can delete products?
    # - Can approve stock?
    # - Can manage users?
    #
    # Those answers come from permissions,
    # never from this model.

    # -----------------------------
    # 8. DESIGN RULES (SOLID ENFORCEMENT)
    # -----------------------------

    # - This model follows SINGLE RESPONSIBILITY:
    #   ONLY stores role information.

    # - It is OPEN for extension:
    #   New roles are added as data,
    #   not by modifying this class.

    # - It depends on abstractions:
    #   Permission resolution happens externally.

    # - It contains NO business logic:
    #   Business services determine what actions
    #   a user may perform.

    pass