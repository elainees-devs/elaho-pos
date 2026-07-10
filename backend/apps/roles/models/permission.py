from django.db import models
from simple_history.models import HistoricalRecords


class Permission(models.Model):
    """
    Permission model.

    Responsibility:
        Store a single system permission that can be assigned to roles.

    This model intentionally does NOT contain:
        - Role assignment logic
        - User authorization logic
        - Business rules

    Those responsibilities belong to dedicated models and services.
    """

    # ------------------------------------------------------------------
    # Permission Information
    # ------------------------------------------------------------------

    # Human-readable permission name.
    name = models.CharField(
        max_length=100,
        help_text="Display name of the permission.",
    )

    # Unique permission identifier used by the system.
    code = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique permission code.",
    )

    # Optional description of what the permission allows.
    description = models.TextField(
        blank=True,
        help_text="Optional description of the permission.",
    )

    # Indicates whether the permission can be assigned.
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether the permission is active.",
    )

    # ------------------------------------------------------------------
    # Audit Information
    # ------------------------------------------------------------------

    # Automatically set when the permission is created.
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp.",
    )

    # Automatically updated whenever the permission changes.
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp.",
    )

    # Track full change history for this model.
    history = HistoricalRecords()

    class Meta:
        db_table = "permissions"
        ordering = ["name"]
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"

    # ------------------------------------------------------------------
    # Model Lifecycle
    # ------------------------------------------------------------------

    def clean(self):
        """
        Normalize permission data before validation.
        """

        if self.name:
            self.name = self.name.strip().title()

        if self.code:
            self.code = self.code.strip().lower()

        super().clean()

    def save(self, *args, **kwargs):
        """
        Normalize and validate data before saving.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    