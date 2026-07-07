from django.db import models

from .role import Role
from .permission import Permission

class RolePermission(models.Model):
    role = models.ForeignKey(
        Role,
        on_delete = models.CASCADE,
        related_name = "permissions"
    )

    permission = models.ForeignKey(
        Permission,
        on_delete = models.CASCADE,
        related_name = "roles"
    )

    # ------------------------------------------------------------------
    # Audit Information
    # ------------------------------------------------------------------

    # Automatically set when the role_permission is created.
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp.",
    )

    # Automatically updated whenever the role_permission changes.
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp.",
    )

    class Meta:
        unique_together = (
            "role",
            "permission"
        )