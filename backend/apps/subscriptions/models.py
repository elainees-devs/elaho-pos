from django.db import models
from simple_history.models import HistoricalRecords


class PlanInterval(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    ANNUAL = "annual", "Annual"


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    EXPIRED = "expired", "Expired"
    SUSPENDED = "suspended", "Suspended"
    CANCELLED = "cancelled", "Cancelled"


class SubscriptionPlan(models.Model):
    """
    SubscriptionPlan model.

    Responsibility:
        Define available subscription tiers and their limits.
    """

    # ------------------------------------------------------------------
    # Plan Information
    # ------------------------------------------------------------------

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Plan name (e.g. Starter, Standard).",
    )

    slug = models.SlugField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="URL-safe identifier.",
    )

    description = models.TextField(
        blank=True,
        help_text="Plan description.",
    )

    # ------------------------------------------------------------------
    # Pricing
    # ------------------------------------------------------------------

    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monthly billing price.",
    )

    annual_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Annual billing price.",
    )

    # ------------------------------------------------------------------
    # Limits
    # ------------------------------------------------------------------

    max_users = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of users allowed.",
    )

    max_branches = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of branches allowed.",
    )

    max_products = models.PositiveIntegerField(
        default=500,
        help_text="Maximum number of products allowed.",
    )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this plan is available for purchase.",
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

    class Meta:
        db_table = "subscription_plans"
        ordering = ["monthly_price"]
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """
    Subscription model.

    Responsibility:
        Track a business's active subscription, linked to a verified payment.
    """

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        db_index=True,
        help_text="Business this subscription belongs to.",
    )

    payment = models.ForeignKey(
        "payments.Payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscriptions",
        help_text="Payment that activated this subscription.",
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
        db_index=True,
        help_text="Subscription plan.",
    )

    # ------------------------------------------------------------------
    # Subscription Details
    # ------------------------------------------------------------------

    billing_cycle = models.CharField(
        max_length=10,
        choices=PlanInterval.choices,
        help_text="Monthly or annual billing.",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount paid for this subscription period.",
    )

    # ------------------------------------------------------------------
    # Duration
    # ------------------------------------------------------------------

    start_date = models.DateField(
        help_text="Subscription start date.",
    )

    end_date = models.DateField(
        db_index=True,
        help_text="Subscription end date.",
    )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
        db_index=True,
        help_text="Current subscription status.",
    )

    auto_renew = models.BooleanField(
        default=False,
        help_text="Whether this subscription should auto-renew.",
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

    class Meta:
        db_table = "subscriptions"
        ordering = ["-created_at"]
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        from django.utils import timezone
        return (
            self.status == SubscriptionStatus.ACTIVE
            and self.start_date <= timezone.now().date() <= self.end_date
        )

    def __str__(self):
        return f"{self.business} - {self.plan.name} ({self.get_status_display()})"
