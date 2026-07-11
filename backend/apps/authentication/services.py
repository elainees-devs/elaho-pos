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

PERMANENT_LOCKOUT_MSG = (
    "Your account has been locked due to repeated failed login attempts. "
    "Kindly contact your system administrator to reactivate your account."
)


class LoginLockoutService:
    """
    Manages login lockout state for user accounts.

    Lifecycle:
    1. Failed attempts increment counter.
    2. At threshold → temporary lockout (10 min) + post_lockout_pending=True.
    3. Lockout expires → one final attempt allowed.
       - Success → reset everything, normal active status.
       - Failure → permanent deactivation (is_active=False).
    4. Permanently locked accounts reject all login attempts.

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
    def is_permanently_locked(user: User) -> bool:
        """
        Check if the account was permanently deactivated by the lockout system.

        Only accounts deactivated via the lockout flow are considered
        permanently locked. Admin-deactivated accounts are excluded.
        """
        return not user.is_active and user.post_lockout_pending

    @staticmethod
    def is_locked_out(user: User) -> bool:
        """
        Check if the user's account is temporarily locked.

        A lockout expires once the current time passes locked_until.
        """
        if user.locked_until is None:
            return False
        return timezone.now() < user.locked_until

    @staticmethod
    def is_lockout_expired(user: User) -> bool:
        """
        Check if the temporary lockout has expired (post-lockout pending).
        """
        if user.locked_until is None:
            return False
        return (
            timezone.now() >= user.locked_until
            and user.post_lockout_pending
        )

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

        If the threshold is reached, lock the account and set
        post_lockout_pending so the next attempt after expiry is final.
        If the post-lockout attempt fails, permanently deactivate.
        """
        user = User.objects.select_for_update().get(pk=user.pk)

        # Post-lockout failed attempt → permanent deactivation.
        if user.post_lockout_pending:
            User.objects.filter(pk=user.pk).update(
                is_active=False,
                failed_login_attempts=0,
                locked_until=None,
            )
            user.refresh_from_db()
            logger.warning(
                "Account permanently deactivated for %s: "
                "failed post-lockout login attempt.",
                user.email,
            )
            return user

        # Normal failed attempt → increment counter.
        new_count = user.failed_login_attempts + 1
        updates = {
            "failed_login_attempts": F("failed_login_attempts") + 1,
        }

        if new_count >= MAX_ATTEMPTS:
            updates["locked_until"] = LoginLockoutService.get_lockout_until()
            updates["post_lockout_pending"] = True
            logger.warning(
                "Account locked for %s after %d failed attempts. "
                "Post-lockout pending.",
                user.email,
                new_count,
            )
        else:
            logger.info(
                "Failed login attempt %d/%d for %s.",
                new_count,
                MAX_ATTEMPTS,
                user.email,
            )

        User.objects.filter(pk=user.pk).update(**updates)
        user.refresh_from_db()
        return user

    @staticmethod
    @transaction.atomic
    def reset_failed_attempts(user: User) -> User:
        """
        Clear the failed login counter, lockout, and post-lockout flag
        on successful login.
        """
        User.objects.filter(pk=user.pk).update(
            failed_login_attempts=0,
            locked_until=None,
            post_lockout_pending=False,
        )
        user.refresh_from_db()
        return user
