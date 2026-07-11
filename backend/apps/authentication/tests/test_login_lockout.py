from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.services import (
    ADMIN_LOCKOUT_MSG,
    LoginLockoutService,
    POST_LOCKOUT_FAIL_MSG,
)

User = get_user_model()

LOGIN_URL = "/api/v1/auth/login/"


class LoginLockoutServiceTest(APITestCase):
    """Unit tests for the LoginLockoutService."""

    def setUp(self):
        self.password = "password123"
        self.user = User.objects.create_user(
            email="user@example.com",
            password=self.password,
            first_name="Test",
            last_name="User",
        )

    def test_requires_admin_unlock_false_when_cycles_low(self):
        self.user.lockout_cycles = 1
        self.user.save(update_fields=["lockout_cycles"])
        self.assertFalse(LoginLockoutService.requires_admin_unlock(self.user))

    def test_requires_admin_unlock_true_at_threshold(self):
        self.user.lockout_cycles = settings.LOGIN_MAX_LOCKOUT_CYCLES
        self.user.save(update_fields=["lockout_cycles"])
        self.assertTrue(LoginLockoutService.requires_admin_unlock(self.user))

    def test_requires_admin_unlock_false_when_zero(self):
        self.assertFalse(LoginLockoutService.requires_admin_unlock(self.user))

    def test_is_locked_out_false_when_no_lockout(self):
        self.assertFalse(LoginLockoutService.is_locked_out(self.user))

    def test_is_locked_out_true_when_within_lockout(self):
        self.user.locked_until = timezone.now() + timedelta(minutes=5)
        self.user.save(update_fields=["locked_until"])
        self.assertTrue(LoginLockoutService.is_locked_out(self.user))

    def test_is_locked_out_false_when_lockout_expired(self):
        self.user.locked_until = timezone.now() - timedelta(minutes=1)
        self.user.save(update_fields=["locked_until"])
        self.assertFalse(LoginLockoutService.is_locked_out(self.user))

    def test_is_lockout_expired_true_when_pending(self):
        self.user.locked_until = timezone.now() - timedelta(minutes=1)
        self.user.post_lockout_pending = True
        self.user.save(update_fields=["locked_until", "post_lockout_pending"])
        self.assertTrue(LoginLockoutService.is_lockout_expired(self.user))

    def test_is_lockout_expired_false_when_not_pending(self):
        self.user.locked_until = timezone.now() - timedelta(minutes=1)
        self.user.post_lockout_pending = False
        self.user.save(update_fields=["locked_until", "post_lockout_pending"])
        self.assertFalse(LoginLockoutService.is_lockout_expired(self.user))

    def test_get_lockout_remaining_seconds_when_locked(self):
        self.user.locked_until = timezone.now() + timedelta(minutes=5)
        self.user.save(update_fields=["locked_until"])
        remaining = LoginLockoutService.get_lockout_remaining_seconds(self.user)
        self.assertGreater(remaining, 290)
        self.assertLessEqual(remaining, 300)

    def test_get_lockout_remaining_seconds_when_not_locked(self):
        remaining = LoginLockoutService.get_lockout_remaining_seconds(self.user)
        self.assertEqual(remaining, 0)

    def test_record_failed_attempt_increments_counter(self):
        LoginLockoutService.record_failed_attempt(self.user)
        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 1)

    def test_record_failed_attempt_locks_at_threshold(self):
        for _ in range(4):
            LoginLockoutService.record_failed_attempt(self.user)

        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 4)
        self.assertIsNone(self.user.locked_until)

        LoginLockoutService.record_failed_attempt(self.user)

        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 5)
        self.assertIsNotNone(self.user.locked_until)
        self.assertTrue(self.user.post_lockout_pending)
        self.assertEqual(self.user.lockout_cycles, 1)
        self.assertTrue(LoginLockoutService.is_locked_out(self.user))

    def test_record_failed_attempt_post_lockout_relocks(self):
        self.user.locked_until = timezone.now() - timedelta(minutes=1)
        self.user.post_lockout_pending = True
        self.user.save(update_fields=["locked_until", "post_lockout_pending"])

        LoginLockoutService.record_failed_attempt(self.user)

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.locked_until)
        self.assertTrue(LoginLockoutService.is_locked_out(self.user))
        self.assertTrue(self.user.post_lockout_pending)
        self.assertEqual(self.user.lockout_cycles, 1)

    def test_record_failed_attempt_increments_lockout_cycles(self):
        self.user.lockout_cycles = 1
        self.user.locked_until = timezone.now() - timedelta(minutes=1)
        self.user.post_lockout_pending = True
        self.user.save(
            update_fields=[
                "lockout_cycles",
                "locked_until",
                "post_lockout_pending",
            ]
        )

        LoginLockoutService.record_failed_attempt(self.user)

        self.user.refresh_from_db()
        self.assertEqual(self.user.lockout_cycles, 2)

    @patch("apps.authentication.services.ADMIN_EMAIL", "admin@example.com")
    @patch("apps.authentication.services.send_mail")
    def test_record_failed_attempt_sends_admin_notification(self, mock_send_mail):
        self.user.locked_until = timezone.now() - timedelta(minutes=1)
        self.user.post_lockout_pending = True
        self.user.save(update_fields=["locked_until", "post_lockout_pending"])

        LoginLockoutService.record_failed_attempt(self.user)

        mock_send_mail.assert_called_once()
        call_kwargs = mock_send_mail.call_args[1]
        self.assertIn("admin@example.com", call_kwargs["recipient_list"])

    @patch("apps.authentication.services.ADMIN_EMAIL", "")
    @patch("apps.authentication.services.send_mail")
    def test_no_notification_when_admin_email_empty(self, mock_send_mail):
        self.user.locked_until = timezone.now() - timedelta(minutes=1)
        self.user.post_lockout_pending = True
        self.user.save(update_fields=["locked_until", "post_lockout_pending"])

        LoginLockoutService.record_failed_attempt(self.user)

        mock_send_mail.assert_not_called()

    def test_reset_failed_attempts_clears_everything(self):
        self.user.failed_login_attempts = 3
        self.user.locked_until = timezone.now() + timedelta(minutes=5)
        self.user.post_lockout_pending = True
        self.user.lockout_cycles = 2
        self.user.save(
            update_fields=[
                "failed_login_attempts",
                "locked_until",
                "post_lockout_pending",
                "lockout_cycles",
            ]
        )

        LoginLockoutService.reset_failed_attempts(self.user)

        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertIsNone(self.user.locked_until)
        self.assertFalse(self.user.post_lockout_pending)
        self.assertEqual(self.user.lockout_cycles, 0)


class LoginViewTest(APITestCase):
    """Integration tests for the login endpoint with escalating lockout."""

    def setUp(self):
        self.password = "password123"
        self.user = User.objects.create_user(
            email="user@example.com",
            password=self.password,
            first_name="Test",
            last_name="User",
        )

    def _lock_user(self):
        """Helper: trigger 5 failed attempts to lock the account."""
        for _ in range(5):
            self.client.post(
                LOGIN_URL,
                {"email": "user@example.com", "password": "wrong"},
                format="json",
            )

    def _expire_lockout(self):
        """Helper: move time past the lockout window."""
        self.user.refresh_from_db()
        self.user.locked_until = timezone.now() - timedelta(minutes=1)
        self.user.save(update_fields=["locked_until"])

    def test_successful_login_returns_tokens(self):
        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_successful_login_resets_failed_attempts(self):
        self.user.failed_login_attempts = 3
        self.user.save(update_fields=["failed_login_attempts"])

        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 0)

    def test_failed_login_returns_401(self):
        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_failed_login_increments_counter(self):
        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 1)

    def test_lockout_after_5_failed_attempts(self):
        self._lock_user()

        self.user.refresh_from_db()
        self.assertTrue(LoginLockoutService.is_locked_out(self.user))
        self.assertTrue(self.user.post_lockout_pending)
        self.assertEqual(self.user.lockout_cycles, 1)

    def test_lockout_blocks_even_correct_password(self):
        self._lock_user()

        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("locked", response.data["detail"].lower())

    def test_lockout_response_includes_retry_after(self):
        self._lock_user()

        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("Try again in", response.data["detail"])

    def test_successful_login_after_lockout_expires(self):
        self._lock_user()
        self._expire_lockout()

        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertIsNone(self.user.locked_until)
        self.assertFalse(self.user.post_lockout_pending)
        self.assertEqual(self.user.lockout_cycles, 0)

    def test_post_lockout_failure_relocks_account(self):
        self._lock_user()
        self._expire_lockout()

        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("locked again", response.data["detail"].lower())

        self.user.refresh_from_db()
        self.assertTrue(LoginLockoutService.is_locked_out(self.user))
        self.assertTrue(self.user.post_lockout_pending)
        self.assertEqual(self.user.lockout_cycles, 2)

    def test_post_lockout_failure_increments_lockout_cycles(self):
        self._lock_user()
        self.user.refresh_from_db()
        self.assertEqual(self.user.lockout_cycles, 1)

        self._expire_lockout()

        self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": "wrong"},
            format="json",
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.lockout_cycles, 2)

    @patch("apps.authentication.services.ADMIN_EMAIL", "admin@example.com")
    @patch("apps.authentication.services.send_mail")
    def test_post_lockout_failure_sends_admin_notification(self, mock_send_mail):
        self._lock_user()
        self._expire_lockout()

        mock_send_mail.reset_mock()

        self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": "wrong"},
            format="json",
        )

        mock_send_mail.assert_called_once()
        call_kwargs = mock_send_mail.call_args[1]
        self.assertIn("admin@example.com", call_kwargs["recipient_list"])

    def test_success_after_lockout_resets_cycles(self):
        self._lock_user()
        self.user.refresh_from_db()
        self.assertEqual(self.user.lockout_cycles, 1)

        self._expire_lockout()

        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.lockout_cycles, 0)
        self.assertFalse(self.user.post_lockout_pending)

    def test_requires_admin_unlock_after_3_cycles(self):
        self.user.lockout_cycles = settings.LOGIN_MAX_LOCKOUT_CYCLES
        self.user.save(update_fields=["lockout_cycles"])

        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("administrator", response.data["detail"].lower())

    def test_admin_required_rejects_correct_password(self):
        self.user.lockout_cycles = settings.LOGIN_MAX_LOCKOUT_CYCLES
        self.user.save(update_fields=["lockout_cycles"])

        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"], ADMIN_LOCKOUT_MSG)

    def test_admin_required_message_mentions_administrator(self):
        self.user.lockout_cycles = settings.LOGIN_MAX_LOCKOUT_CYCLES
        self.user.save(update_fields=["lockout_cycles"])

        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("administrator", response.data["detail"].lower())
        self.assertIn("unlock", response.data["detail"].lower())

    def test_nonexistent_email_returns_same_error(self):
        response = self.client.post(
            LOGIN_URL,
            {"email": "nobody@example.com", "password": "password123"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Invalid email or password.")

    def test_inactive_user_returns_generic_error(self):
        User.objects.create_user(
            email="inactive@example.com",
            password=self.password,
            first_name="Inactive",
            last_name="User",
            is_active=False,
        )
        response = self.client.post(
            LOGIN_URL,
            {"email": "inactive@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Invalid email or password.")

    def test_missing_fields_returns_400(self):
        response = self.client.post(LOGIN_URL, {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_get_method_returns_405(self):
        response = self.client.get(LOGIN_URL)
        self.assertEqual(response.status_code, 405)

    def test_successful_login_does_not_lock(self):
        for _ in range(4):
            self.client.post(
                LOGIN_URL,
                {"email": "user@example.com", "password": "wrong"},
                format="json",
            )

        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertIsNone(self.user.locked_until)

    def test_mixed_attempts_then_success_resets(self):
        for _ in range(3):
            self.client.post(
                LOGIN_URL,
                {"email": "user@example.com", "password": "wrong"},
                format="json",
            )

        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 3)

        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 0)

    def test_full_escalation_cycle(self):
        """End-to-end: 5 failures → lock → fail → lock → fail → fail3 cycles → admin required."""
        # Cycle 1: 5 failures → lock
        self._lock_user()
        self.user.refresh_from_db()
        self.assertEqual(self.user.lockout_cycles, 1)

        # Cycle 2: post-lockout failure → re-lock
        self._expire_lockout()
        self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": "wrong"},
            format="json",
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.lockout_cycles, 2)

        # Cycle 3: post-lockout failure → re-lock, now at threshold
        self._expire_lockout()
        self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": "wrong"},
            format="json",
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.lockout_cycles, 3)

        # Any further login → 403 admin required
        self._expire_lockout()
        response = self.client.post(
            LOGIN_URL,
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
