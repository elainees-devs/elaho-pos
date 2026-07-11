from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """
    User model.

    Responsibility:
        Store the identity and account state of a system user.

    This model intentionally does NOT contain:
        - Role or permission logic
        - Business rules
        - Application workflows

    Those responsibilities belong to dedicated models and services.
    """

    # Remove username authentication.
    username = None

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    # Email is used as the unique login identifier.
    email = models.EmailField(
        unique=True,
        help_text="Unique email address used for authentication.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # ------------------------------------------------------------------
    # Login Security
    # ------------------------------------------------------------------

    # Tracks consecutive failed login attempts.
    failed_login_attempts = models.PositiveSmallIntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts.",
    )

    # Timestamp when the lockout expires. Null = not locked.
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Account is locked until this timestamp.",
    )

    # ------------------------------------------------------------------
    # Personal Information
    # ------------------------------------------------------------------

    first_name = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(2)],
        help_text="User's first name.",
    )

    last_name = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(2)],
        help_text="User's last name.",
    )

    # Optional contact number.
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Optional phone number.",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    # Business role assigned to the user.
    # Authorization is resolved elsewhere.
    role = models.ForeignKey(
        "roles.Role",
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
        db_index=True,
        help_text="Assigned role.",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Indicates whether the user account is active.",
    )

    # ------------------------------------------------------------------
    # Audit Information
    # ------------------------------------------------------------------

    # Automatically updated whenever the user record changes.
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp.",
    )

    # Soft-delete flag.
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Indicates whether the user has been archived.",
    )

    # Custom manager supporting email authentication.
    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["first_name", "last_name"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    # ------------------------------------------------------------------
    # Model Lifecycle
    # ------------------------------------------------------------------

    def clean(self):
        """
        Normalize user data before validation.
        """

        # Normalize first
        if self.email:
            self.email = self.email.strip().lower()

        if self.first_name:
            self.first_name = self.first_name.strip().title()

        if self.last_name:
            self.last_name = self.last_name.strip().title()

        # Then run Django validation
        super().clean()

    def save(self, *args, **kwargs):
        """
        Normalize and validate data before saving.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # Read-only Properties
    # ------------------------------------------------------------------

    @property
    def full_name(self):
        """
        Returns the user's full name.
        """
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def created_at(self):
        """
        Alias for the account creation timestamp.
        """
        return self.date_joined

    # ------------------------------------------------------------------
    # String Representation
    # ------------------------------------------------------------------

    def __str__(self):
        """
        Human-readable representation of the user.
        """
        return self.full_name or self.email