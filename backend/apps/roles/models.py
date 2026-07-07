from django.db import models


class Role(models.Model):
    """
    Role model.

    Responsibility:
        Store role information only.

    A role groups users under a common category (e.g. SuperAdmin,
    Manager, Staff). It does not determine permissions or application
    behavior. Authorization is handled by the permission and service
    layers.
    """

    # ------------------------------------------------------------------
    # Role Information
    # ------------------------------------------------------------------

    # Unique role name.
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique role name.",
    )

    # Optional description of the role.
    description = models.TextField(
        blank=True,
        help_text="Optional role description.",
    )

    # Optional hierarchy used for sorting or display.
    # Higher values represent higher-level roles.
    level = models.PositiveSmallIntegerField(
        default=1,
        help_text="Role hierarchy level.",
    )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    # Indicates whether the role can be assigned to users.
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the role is active.",
    )

    # ------------------------------------------------------------------
    # Audit Information
    # ------------------------------------------------------------------

    # Automatically set when the role is created.
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp.",
    )

    # Automatically updated whenever the role changes.
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp.",
    )

    class Meta:
        db_table = "roles"
        ordering = ["-level", "name"]
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    # ------------------------------------------------------------------
    # Model Lifecycle
    # ------------------------------------------------------------------

    def clean(self):
        """
        Normalize role data before validation.
        """
        super().clean()

        if self.name:
            self.name = self.name.strip().title()

        if self.description:
            self.description = self.description.strip()

    def save(self, *args, **kwargs):
        """
        Validate and normalize data before saving.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # String Representation
    # ------------------------------------------------------------------

    def __str__(self):
        """
        Human-readable representation of the role.
        """
        return self.name