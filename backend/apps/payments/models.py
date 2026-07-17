import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"
    REFUNDED = "refunded", "Refunded"


class PaymentMethod(models.TextChoices):
    MPESA = "mpesa", "M-Pesa"
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    CASH = "cash", "Cash"
    CARD = "card", "Card"
    AIRTEL_MONEY = "airtel_money", "Airtel Money"
    OTHER = "other", "Other"


class BillingCycle(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    ANNUAL = "annual", "Annual"


class AuditAction(models.TextChoices):
    CREATED = "created", "Created"
    VERIFIED = "verified", "Verified"
    INVITATION_SENT = "invitation_sent", "Invitation Sent"
    INVITATION_RESENT = "invitation_resent", "Invitation Resent"
    CANCELLED = "cancelled", "Cancelled"
    REFUNDED = "refunded", "Refunded"
    UPDATED = "updated", "Updated"


class Payment(models.Model):
    """
    Payment model.

    Responsibility:
        Store a record of an externally processed payment. The system does
        not process payments — it only records and verifies them.

    Lifecycle:
        1. Super Admin creates a payment record (status=Pending).
        2. Super Admin verifies the payment externally.
        3. Super Admin marks the payment as Paid.
        4. A RegistrationInvitation is generated and emailed to the owner.
        5. Owner registers via the invitation link.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    uuid = models.UUIDField(
        default=secrets.token_urlsafe,
        unique=True,
        db_index=True,
        help_text="Public unique identifier for this payment.",
    )

    # ------------------------------------------------------------------
    # Owner Information
    # ------------------------------------------------------------------

    owner_name = models.CharField(
        max_length=150,
        help_text="Full name of the business owner.",
    )

    owner_email = models.EmailField(
        help_text="Email address of the business owner.",
    )

    owner_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number of the business owner.",
    )

    # ------------------------------------------------------------------
    # Business Information
    # ------------------------------------------------------------------

    business_name = models.CharField(
        max_length=100,
        help_text="Name of the business being registered.",
    )

    # ------------------------------------------------------------------
    # Subscription Details
    # ------------------------------------------------------------------

    subscription_plan = models.ForeignKey(
        "subscriptions.SubscriptionPlan",
        on_delete=models.PROTECT,
        related_name="payments",
        db_index=True,
        help_text="Subscription plan selected.",
    )

    billing_cycle = models.CharField(
        max_length=10,
        choices=BillingCycle.choices,
        help_text="Monthly or annual billing.",
    )

    # ------------------------------------------------------------------
    # Payment Details
    # ------------------------------------------------------------------

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Payment amount.",
    )

    currency = models.CharField(
        max_length=3,
        default="KES",
        help_text="ISO 4217 currency code.",
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        help_text="External payment method used.",
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Transaction or reference number from the external payment.",
    )

    payment_date = models.DateField(
        help_text="Date the payment was made externally.",
    )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
        help_text="Current payment status.",
    )

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the payment was verified.",
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_payments",
        help_text="Super Admin who verified this payment.",
    )

    # ------------------------------------------------------------------
    # Notes
    # ------------------------------------------------------------------

    notes = models.TextField(
        blank=True,
        help_text="Optional notes about the payment.",
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
        db_table = "payments"
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    # ------------------------------------------------------------------
    # Model Lifecycle
    # ------------------------------------------------------------------

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # Read-only Properties
    # ------------------------------------------------------------------

    @property
    def is_verifiable(self):
        return self.status == PaymentStatus.PENDING

    @property
    def is_cancellable(self):
        return self.status in (PaymentStatus.PENDING, PaymentStatus.PAID)

    @property
    def is_refundable(self):
        return self.status == PaymentStatus.PAID

    # ------------------------------------------------------------------
    # String Representation
    # ------------------------------------------------------------------

    def __str__(self):
        return f"Payment {self.uuid} - {self.business_name} ({self.get_status_display()})"


class RegistrationInvitation(models.Model):
    """
    RegistrationInvitation model.

    Responsibility:
        Store a secure invitation token sent to a business owner after
        their payment is verified. The token allows them to register
        their business and create their account.

    Lifecycle:
        1. Generated when a payment is verified.
        2. Raw token is emailed to the owner.
        3. Owner clicks the link; token is validated.
        4. Business, User, Branch, Subscription are created.
        5. Invitation is marked as used.
    """

    # ------------------------------------------------------------------
    # Payment Link
    # ------------------------------------------------------------------

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name="invitation",
        db_index=True,
        help_text="Payment that generated this invitation.",
    )

    # ------------------------------------------------------------------
    # Invitation Target
    # ------------------------------------------------------------------

    email = models.EmailField(
        db_index=True,
        help_text="Email address to send the invitation to.",
    )

    owner_name = models.CharField(
        max_length=150,
        help_text="Name of the business owner.",
    )

    business_name = models.CharField(
        max_length=100,
        help_text="Name of the business being registered.",
    )

    # ------------------------------------------------------------------
    # Token
    # ------------------------------------------------------------------

    token_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="SHA-256 hash of the raw invitation token.",
    )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    is_used = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this invitation has been used.",
    )

    # ------------------------------------------------------------------
    # Expiry
    # ------------------------------------------------------------------

    expires_at = models.DateTimeField(
        help_text="Timestamp after which this invitation expires.",
    )

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_registration_invitations",
        help_text="Super Admin who created this invitation.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp.",
    )

    history = HistoricalRecords()

    class Meta:
        db_table = "registration_invitations"
        ordering = ["-created_at"]
        verbose_name = "Registration Invitation"
        verbose_name_plural = "Registration Invitations"

    # ------------------------------------------------------------------
    # Token Operations
    # ------------------------------------------------------------------

    @staticmethod
    def generate_raw_token() -> str:
        return secrets.token_urlsafe(48)

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()

    def is_valid(self) -> bool:
        return not self.is_used and timezone.now() < self.expires_at

    def mark_used(self) -> None:
        self.is_used = True
        self.save(update_fields=["is_used"])

    # ------------------------------------------------------------------
    # Convenience Constructors
    # ------------------------------------------------------------------

    @classmethod
    def create_for_payment(cls, payment, created_by, expiry_hours=48):
        """
        Create a registration invitation for a verified payment.
        Returns (instance, raw_token).
        """
        raw_token = cls.generate_raw_token()
        token_hash = cls.hash_token(raw_token)

        instance = cls.objects.create(
            payment=payment,
            email=payment.owner_email,
            owner_name=payment.owner_name,
            business_name=payment.business_name,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(hours=expiry_hours),
            created_by=created_by,
        )

        return instance, raw_token

    @classmethod
    def validate_token(cls, raw_token):
        """
        Validate a raw token. Returns the invitation instance or None.
        Eagerly loads payment and subscription_plan for downstream use.
        """
        token_hash = cls.hash_token(raw_token)

        try:
            instance = cls.objects.select_related(
                "payment",
                "payment__subscription_plan",
            ).get(
                token_hash=token_hash,
                is_used=False,
            )
        except cls.DoesNotExist:
            return None

        return instance if instance.is_valid() else None

    # ------------------------------------------------------------------
    # String Representation
    # ------------------------------------------------------------------

    def __str__(self):
        return f"Invitation for {self.email} ({self.business_name})"


class PaymentAuditLog(models.Model):
    """
    PaymentAuditLog model.

    Responsibility:
        Record all payment-related actions for audit and compliance.
    """

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="audit_logs",
        db_index=True,
        help_text="Payment this log entry belongs to.",
    )

    # ------------------------------------------------------------------
    # Action
    # ------------------------------------------------------------------

    action = models.CharField(
        max_length=20,
        choices=AuditAction.choices,
        help_text="Action performed on the payment.",
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payment_audit_logs",
        help_text="User who performed this action.",
    )

    description = models.TextField(
        blank=True,
        help_text="Human-readable description of the action.",
    )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When this action was performed.",
    )

    class Meta:
        db_table = "payment_audit_logs"
        ordering = ["-timestamp"]
        verbose_name = "Payment Audit Log"
        verbose_name_plural = "Payment Audit Logs"

    def __str__(self):
        return f"{self.action} on {self.payment.uuid} by {self.performed_by}"
