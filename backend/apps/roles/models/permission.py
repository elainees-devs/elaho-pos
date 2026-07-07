from django.db import models

class Permission(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

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


    def __str__(self):
        return self.name