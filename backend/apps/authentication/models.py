import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

User = get_user_model()

TOKEN_EXPIRY_HOURS = getattr(settings, "VERIFICATION_TOKEN_EXPIRY_HOURS", 24)


class TokenPurpose(models.TextChoices):
    EMAIL_VERIFICATION = "email_verification", "Email Verification"
    PASSWORD_RESET = "password_reset", "Password Reset"


class VerificationToken(models.Model):
    """
    VerificationToken model.

    Responsibility:
        Store hashed verification tokens for email verification and
        password reset flows.

    Tokens are stored as SHA-256 hashes. The raw token is returned to
    the user (via email) and never persisted in plaintext.

    Lifecycle:
        1. Generate a random token and store its hash.
        2. Send the raw token to the user via email.
        3. User submits the token; hash it and compare against stored hash.
        4. Mark as used on successful validation.
    """

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="verification_tokens",
        db_index=True,
        help_text="User this token belongs to.",
    )

    # ------------------------------------------------------------------
    # Token
    # ------------------------------------------------------------------

    # SHA-256 hash of the raw token. Raw token is never stored.
    token_hash = models.CharField(
        max_length=64,
        help_text="SHA-256 hash of the raw verification token.",
    )

    # Categorizes the token's purpose.
    purpose = models.CharField(
        max_length=20,
        choices=TokenPurpose.choices,
        help_text="Purpose of this verification token.",
    )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    is_used = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this token has been consumed.",
    )

    # ------------------------------------------------------------------
    # Expiry
    # ------------------------------------------------------------------

    expires_at = models.DateTimeField(
        help_text="Timestamp after which this token is no longer valid.",
    )

    # ------------------------------------------------------------------
    # Audit Information
    # ------------------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp.",
    )

    # IP address of the client that requested the token.
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the client that requested this token.",
    )

    user_agent = models.CharField(
        max_length=512,
        blank=True,
        help_text="User-Agent header of the client that requested this token.",
    )

    history = HistoricalRecords()

    class Meta:
        db_table = "verification_tokens"
        ordering = ["-created_at"]
        verbose_name = "Verification Token"
        verbose_name_plural = "Verification Tokens"
        indexes = [
            models.Index(
                fields=["user", "purpose"],
                name="idx_vtoken_user_purpose",
            ),
        ]

    # ------------------------------------------------------------------
    # Model Lifecycle
    # ------------------------------------------------------------------

    def clean(self):
        """
        Normalize data before validation.
        """
        super().clean()

    def save(self, *args, **kwargs):
        """
        Validate and normalize data before saving.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # Token Operations
    # ------------------------------------------------------------------

    @staticmethod
    def generate_raw_token() -> str:
        """
        Generate a cryptographically secure random token.
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(raw_token: str) -> str:
        """
        Produce a SHA-256 hex digest of the raw token.
        """
        return hashlib.sha256(raw_token.encode()).hexdigest()

    def is_valid(self) -> bool:
        """
        Check if the token is unused and not expired.
        """
        return not self.is_used and timezone.now() < self.expires_at

    def mark_used(self) -> None:
        """
        Mark the token as consumed and persist.
        """
        self.is_used = True
        self.save(update_fields=["is_used"])

    # ------------------------------------------------------------------
    # Convenience Constructors
    # ------------------------------------------------------------------

    @classmethod
    def create_for_user(
        cls,
        user,
        purpose: str,
        ip_address: str | None = None,
        user_agent: str = "",
        expiry_hours: int | None = None,
    ) -> tuple["VerificationToken", str]:
        """
        Create a verification token for a user.

        Invalidates any existing unused tokens for the same user + purpose.
        Returns a tuple of (token_instance, raw_token).

        The raw_token must be sent to the user via email and is never
        stored in the database.
        """
        hours = expiry_hours or TOKEN_EXPIRY_HOURS

        # Invalidate previous unused tokens for this user + purpose.
        cls.objects.filter(
            user=user,
            purpose=purpose,
            is_used=False,
        ).update(is_used=True)

        raw_token = cls.generate_raw_token()
        token_hash = cls.hash_token(raw_token)

        instance = cls.objects.create(
            user=user,
            token_hash=token_hash,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(hours=hours),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return instance, raw_token

    @classmethod
    def validate_token(
        cls,
        user,
        raw_token: str,
        purpose: str,
    ) -> "VerificationToken | None":
        """
        Validate a raw token against stored hashes.

        Returns the matching VerificationToken instance if valid,
        or None if no valid token exists.
        """
        token_hash = cls.hash_token(raw_token)

        try:
            instance = cls.objects.get(
                user=user,
                token_hash=token_hash,
                purpose=purpose,
                is_used=False,
            )
        except cls.DoesNotExist:
            return None

        if not instance.is_valid():
            return None

        return instance

    # ------------------------------------------------------------------
    # String Representation
    # ------------------------------------------------------------------

    def __str__(self):
        """
        Human-readable representation of the token.
        """
        return f"{self.get_purpose_display()} for {self.user}"
