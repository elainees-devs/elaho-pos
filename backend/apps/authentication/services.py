import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from django.utils import timezone

User = get_user_model()

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = getattr(settings, "LOGIN_MAX_FAILED_ATTEMPTS", 5)
LOCKOUT_MINUTES = getattr(settings, "LOGIN_LOCKOUT_DURATION_MINUTES", 10)


class LoginLockoutService:
    """
    Manages login lockout state for user accounts.

    Thread-safe via F() expressions and select_for_update() to prevent
    race conditions on concurrent failed login attempts.
    """

    @staticmethod
    def _get_user_for_login(email: str) -> User | None:
        """
        Retrieve a user by email for login processing.
        Uses select_for_update to lock the row during concurrent writes.
        """
        try:
            return User.objects.select_for_update().get(
                email__iexact=email.strip()
            )
        except User.DoesNotExist:
            return None

    @staticmethod
    def is_locked_out(user: User) -> bool:
        """
        Check if the user's account is currently locked.

        A lockout expires once the current time passes locked_until.
        """
        if user.locked_until is None:
            return False
        return timezone.now() < user.locked_until

    @staticmethod
    def get_lockout_remaining_seconds(user: User) -> int:
        """
        Return seconds remaining in lockout, or 0 if not locked.
        """
        if user.locked_until is None:
            return 0
        remaining = user.locked_until - timezone.now()
        return max(0, int(remaining.total_seconds()))

    @staticmethod
    def get_lockout_until() -> timezone.datetime:
        """
        Calculate the lockout expiration timestamp.
        """
        return timezone.now() + timedelta(minutes=LOCKOUT_MINUTES)

    @staticmethod
    @transaction.atomic
    def record_failed_attempt(user: User) -> User:
        """
        Increment the failed login counter.

        If the threshold is reached, lock the account.
        Uses F() to prevent race conditions on concurrent increments.
        """
        updates = {"failed_login_attempts": F("failed_login_attempts") + 1}

        # Re-fetch fresh count after increment for threshold check.
        user = User.objects.select_for_update().get(pk=user.pk)
        new_count = user.failed_login_attempts + 1

        if new_count >= MAX_ATTEMPTS:
            updates["locked_until"] = LoginLockoutService.get_lockout_until()
            logger.warning(
                "Account locked for %s after %d failed attempts.",
                user.email,
                new_count,
            )

        User.objects.filter(pk=user.pk).update(**updates)
        user.refresh_from_db()

        logger.info(
            "Failed login attempt %d/%d for %s.",
            user.failed_login_attempts,
            MAX_ATTEMPTS,
            user.email,
        )
        return user

    @staticmethod
    @transaction.atomic
    def reset_failed_attempts(user: User) -> User:
        """
        Clear the failed login counter and lockout on successful login.
        """
        User.objects.filter(pk=user.pk).update(
            failed_login_attempts=0,
            locked_until=None,
        )
        user.refresh_from_db()
        return user
