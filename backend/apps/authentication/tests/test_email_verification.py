from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.models import TokenPurpose, VerificationToken

User = get_user_model()


class SendVerificationEmailTest(APITestCase):
    """Tests for POST /api/v1/auth/send-verification/"""

    def setUp(self):
        self.url = "/api/v1/auth/send-verification/"
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def _auth_header(self):
        return f"Bearer {self.access_token}"

    @patch("apps.authentication.serializers.send_mail")
    def test_send_verification_authenticated(self, mock_send_mail):
        response = self.client.post(
            self.url,
            format="json",
            HTTP_AUTHORIZATION=self._auth_header(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "Verification email sent.")
        mock_send_mail.assert_called_once()

    def test_send_verification_unauthenticated(self):
        response = self.client.post(self.url, format="json")
        self.assertEqual(response.status_code, 403)

    @patch("apps.authentication.serializers.send_mail")
    def test_send_verification_already_verified(self, mock_send_mail):
        self.user.email_verified = True
        self.user.save(update_fields=["email_verified"])

        response = self.client.post(
            self.url,
            format="json",
            HTTP_AUTHORIZATION=self._auth_header(),
        )
        self.assertEqual(response.status_code, 200)
        mock_send_mail.assert_not_called()

    @patch("apps.authentication.serializers.send_mail")
    def test_send_verification_email_contains_link(self, mock_send_mail):
        response = self.client.post(
            self.url,
            format="json",
            HTTP_AUTHORIZATION=self._auth_header(),
        )
        self.assertEqual(response.status_code, 200)

        call_kwargs = mock_send_mail.call_args[1]
        html_body = call_kwargs.get("html_message", "")
        text_body = call_kwargs.get("message", "")
        self.assertIn("verify-email", text_body)
        self.assertIn("token=", text_body)
        self.assertIn("email=", text_body)
        self.assertIn("verify-email", html_body)

    @patch("apps.authentication.serializers.send_mail")
    def test_send_verification_creates_token(self, mock_send_mail):
        response = self.client.post(
            self.url,
            format="json",
            HTTP_AUTHORIZATION=self._auth_header(),
        )
        self.assertEqual(response.status_code, 200)

        token_exists = VerificationToken.objects.filter(
            user=self.user,
            purpose=TokenPurpose.EMAIL_VERIFICATION,
            is_used=False,
        ).exists()
        self.assertTrue(token_exists)

    @patch("apps.authentication.serializers.send_mail")
    def test_send_verification_invalidates_old_tokens(self, mock_send_mail):
        # Create an old token
        old_token_instance, _ = VerificationToken.create_for_user(
            user=self.user,
            purpose=TokenPurpose.EMAIL_VERIFICATION,
        )

        # Request a new one
        response = self.client.post(
            self.url,
            format="json",
            HTTP_AUTHORIZATION=self._auth_header(),
        )
        self.assertEqual(response.status_code, 200)

        # Old token should be marked as used
        old_token_instance.refresh_from_db()
        self.assertTrue(old_token_instance.is_used)

    def test_send_verification_get_returns_405(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=self._auth_header(),
        )
        self.assertEqual(response.status_code, 405)

    @patch("apps.authentication.serializers.send_mail")
    def test_send_verification_inactive_user(self, mock_send_mail):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        response = self.client.post(
            self.url,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        # Inactive users get 401 from JWT auth
        self.assertIn(response.status_code, [401, 403])


class VerifyEmailTest(APITestCase):
    """Tests for POST /api/v1/auth/verify-email/"""

    def setUp(self):
        self.url = "/api/v1/auth/verify-email/"
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )
        self.token_instance, self.raw_token = VerificationToken.create_for_user(
            user=self.user,
            purpose=TokenPurpose.EMAIL_VERIFICATION,
        )

    def test_verify_with_valid_token(self):
        response = self.client.post(
            self.url,
            {"token": self.raw_token, "email": "user@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "Email verified successfully.")

        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

        self.token_instance.refresh_from_db()
        self.assertTrue(self.token_instance.is_used)

    def test_verify_with_invalid_token(self):
        response = self.client.post(
            self.url,
            {"token": "invalid-token", "email": "user@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_verify_with_expired_token(self):
        # Create an expired token
        self.token_instance.expires_at = timezone.now() - timedelta(hours=1)
        self.token_instance.save(update_fields=["expires_at"])

        response = self.client.post(
            self.url,
            {"token": self.raw_token, "email": "user@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_verify_with_wrong_email(self):
        response = self.client.post(
            self.url,
            {"token": self.raw_token, "email": "wrong@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_verify_already_verified(self):
        self.user.email_verified = True
        self.user.save(update_fields=["email_verified"])

        response = self.client.post(
            self.url,
            {"token": self.raw_token, "email": "user@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "Email is already verified.")

    def test_verify_get_returns_405(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_verify_with_missing_fields(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_verify_with_inactive_user(self):
        inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password="password123",
            first_name="Inactive",
            last_name="User",
            is_active=False,
        )

        response = self.client.post(
            self.url,
            {"token": "any-token", "email": "inactive@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_verify_used_token_rejected(self):
        # Use the token once
        self.client.post(
            self.url,
            {"token": self.raw_token, "email": "user@example.com"},
            format="json",
        )

        # Try to use it again
        self.user.email_verified = False
        self.user.save(update_fields=["email_verified"])

        response = self.client.post(
            self.url,
            {"token": self.raw_token, "email": "user@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    @patch("apps.authentication.serializers.send_mail")
    def test_full_flow_send_then_verify(self, mock_send_mail):
        # Step 1: Send verification (as authenticated user)
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        send_response = self.client.post(
            "/api/v1/auth/send-verification/",
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(send_response.status_code, 200)

        # Extract token from email
        call_kwargs = mock_send_mail.call_args[1]
        text_body = call_kwargs.get("message", "")

        # Parse token from email body (format: ...token=<token>&email=...)
        token_start = text_body.find("token=") + 6
        token_end = text_body.find("&", token_start)
        if token_end == -1:
            token_end = text_body.find("\n", token_start)
        raw_token = text_body[token_start:token_end].strip()

        # Step 2: Verify email (as unauthenticated)
        verify_response = self.client.post(
            self.url,
            {"token": raw_token, "email": "user@example.com"},
            format="json",
        )
        self.assertEqual(verify_response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
