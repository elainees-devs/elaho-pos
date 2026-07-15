import secrets

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.text import slugify
from simple_history.models import HistoricalRecords


class Business(models.Model):
    """
    Business model.

    Responsibility:
        Represent a tenant entity — the organizational boundary for
        users, inventory, sales, and all POS data.

    This model intentionally does NOT contain:
        - User management logic
        - Inventory or sales rules
        - Subscription or billing logic

    Those responsibilities belong to dedicated models and services.
    """

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="Business display name.",
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="URL-safe identifier, auto-generated from name.",
    )

    # ------------------------------------------------------------------
    # Ownership
    # ------------------------------------------------------------------

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_businesses",
        null=True,
        blank=True,
        db_index=True,
        help_text="Business owner. Set after the owner user is created.",
    )

    # ------------------------------------------------------------------
    # Contact Information
    # ------------------------------------------------------------------

    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Business contact phone number.",
    )

    email = models.EmailField(
        blank=True,
        help_text="Business contact email address.",
    )

    address = models.TextField(
        blank=True,
        help_text="Physical address of the business.",
    )
    kra_pin=models.CharField(
        max_length=20,
        blank=False,
        help_text="Business KRA Pin"
    )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this business is active.",
    )

    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Soft-delete flag.",
    )

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp.",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp.",
    )

    history = HistoricalRecords()

    # ------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------

    class Meta:
        db_table = "businesses"
        ordering = ["name"]
        verbose_name = "Business"
        verbose_name_plural = "Businesses"

    # ------------------------------------------------------------------
    # Model Lifecycle
    # ------------------------------------------------------------------

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_slug()
        self.full_clean()
        super().save(*args, **kwargs)

    def _generate_slug(self) -> str:
        base = slugify(self.name)
        slug = base
        while Business.objects.filter(slug=slug).exists():
            slug = f"{base}-{secrets.token_hex(3)}"
        return slug

    # ------------------------------------------------------------------
    # String Representation
    # ------------------------------------------------------------------

    def __str__(self):
        return self.name
