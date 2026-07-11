import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.template.loader import render_to_string
from django.utils import timezone

User = get_user_model()

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = getattr(settings, "LOGIN_MAX_FAILED_ATTEMPTS", 5)
LOCKOUT_MINUTES = getattr(settings, "LOGIN_LOCKOUT_DURATION_MINUTES", 10)
MAX_LOCKOUT_CYCLES = getattr(settings, "LOGIN_MAX_LOCKOUT_CYCLES", 3)
ADMIN_EMAIL = getattr(settings, "LOGIN_ADMIN_EMAIL", "")

ADMIN_LOCKOUT_MSG = (
    "Your account has been locked due to repeated failed login attempts. "
    "Kindly contact your system administrator to unlock your account."
)

POST_LOCKOUT_FAIL_MSG = (
    "Incorrect password. Your account has been locked again for security. "
    "If this continues, administrator intervention may be required."
)


class LoginLockoutService:
    """
    Manages login lockout state for user accounts with escalating lockout cycles.

    Lifecycle:
    1. Failed attempts increment counter.
    2. At threshold (5) → temporary lockout (10 min) + post_lockout_pending=True.
       lockout_cycles increments on each lockout trigger.
    3. Lockout expires → one final attempt allowed.
       - Success → reset everything (including lockout_cycles), normal active status.
       - Failure → re-lock for another 10 min, lockout_cycles increments again,
         admin notified. If lockout_cycles >= MAX_LOCKOUT_CYCLES, account requires
         admin unlock (all logins blocked).
    4. Admin-unlocked accounts are fully restored.

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
    def requires_admin_unlock(user: User) -> bool:
        """
        Check if the account has exceeded the lockout cycle threshold
        and requires administrator intervention to unlock.
        """
        return user.lockout_cycles >= MAX_LOCKOUT_CYCLES

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
        If the post-lockout attempt fails, re-lock the account,
        increment lockout_cycles, and notify the admin.
        """
        user = User.objects.select_for_update().get(pk=user.pk)

        # Post-lockout failed attempt → re-lock with escalating cycles.
        if user.post_lockout_pending:
            updates = {
                "locked_until": LoginLockoutService.get_lockout_until(),
                "lockout_cycles": F("lockout_cycles") + 1,
            }
            User.objects.filter(pk=user.pk).update(**updates)
            user.refresh_from_db()
            logger.warning(
                "Account re-locked for %s (cycle %d/%d): "
                "failed post-lockout login attempt.",
                user.email,
                user.lockout_cycles,
                MAX_LOCKOUT_CYCLES,
            )
            LoginLockoutService._notify_admin(user)
            return user

        # Normal failed attempt → increment counter.
        new_count = user.failed_login_attempts + 1
        updates = {
            "failed_login_attempts": F("failed_login_attempts") + 1,
        }

        if new_count >= MAX_ATTEMPTS:
            updates["locked_until"] = LoginLockoutService.get_lockout_until()
            updates["post_lockout_pending"] = True
            updates["lockout_cycles"] = F("lockout_cycles") + 1
            logger.warning(
                "Account locked for %s after %d failed attempts. "
                "Lockout cycle %d.",
                user.email,
                new_count,
                user.lockout_cycles + 1,
            )
            LoginLockoutService._notify_admin(user)
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
        Clear the failed login counter, lockout, post-lockout flag,
        and lockout cycles on successful login.
        """
        User.objects.filter(pk=user.pk).update(
            failed_login_attempts=0,
            locked_until=None,
            post_lockout_pending=False,
            lockout_cycles=0,
        )
        user.refresh_from_db()
        return user

    @staticmethod
    def _notify_admin(user: User) -> None:
        """
        Send an email notification to the administrator when an account
        is locked or re-locked. Silently skipped if LOGIN_ADMIN_EMAIL is empty.
        """
        if not ADMIN_EMAIL:
            return

        try:
            context = {
                "user": user,
                "lockout_cycles": user.lockout_cycles,
                "max_cycles": MAX_LOCKOUT_CYCLES,
                "timestamp": timezone.now(),
            }

            subject = render_to_string(
                "authentication/admin_lockout_subject.txt", context
            ).strip()
            html_body = render_to_string(
                "authentication/admin_lockout_body.html", context
            )
            text_body = render_to_string(
                "authentication/admin_lockout_body.txt", context
            )

            send_mail(
                subject=subject,
                message=text_body,
                html_message=html_body,
                from_email=None,
                recipient_list=[ADMIN_EMAIL],
            )
        except Exception:
            logger.exception(
                "Failed to send admin lockout notification for %s.",
                user.email,
            )
