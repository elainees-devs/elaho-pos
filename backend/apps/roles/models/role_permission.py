from django.db import models
from simple_history.models import HistoricalRecords

from .permission import Permission
from .role import Role


class RolePermission(models.Model):
    """
    RolePermission model.

    Responsibility:
        Represent the assignment of a permission to a role.

    This model intentionally does NOT contain:
        - Authorization logic
        - User assignment logic
        - Business rules

    Those responsibilities belong to dedicated models and services.
    """

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    # Role receiving the permission.
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="permissions",
        db_index=True,
        help_text="Role assigned to the permission.",
    )

    # Permission assigned to the role.
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="roles",
        db_index=True,
        help_text="Permission granted to the role.",
    )

    # ------------------------------------------------------------------
    # Audit Information
    # ------------------------------------------------------------------

    # Automatically set when the assignment is created.
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp.",
    )

    # Automatically updated whenever the assignment changes.
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp.",
    )

    # Track full change history for this model.
    history = HistoricalRecords()

    class Meta:
        db_table = "role_permissions"
        ordering = ["role", "permission"]
        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"
        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="unique_role_permission",
            )
        ]

    # ------------------------------------------------------------------
    # Model Lifecycle
    # ------------------------------------------------------------------

    def clean(self):
        """
        Validate the role-permission assignment.
        """
        super().clean()

    def save(self, *args, **kwargs):
        """
        Validate data before saving.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # String Representation
    # ------------------------------------------------------------------

    def __str__(self):
        """
        Human-readable representation of the assignment.
        """
        return f"{self.role} → {self.permission}"