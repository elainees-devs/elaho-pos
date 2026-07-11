from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

token_generator = PasswordResetTokenGenerator()


class PasswordResetRequestTest(APITestCase):
    def setUp(self):
        self.url = "/api/v1/auth/password-reset/"
        self.password = "password123"
        self.user = User.objects.create_user(
            email="user@example.com",
            password=self.password,
            first_name="Test",
            last_name="User",
        )

    @patch("apps.authentication.serializers.send_mail")
    def test_request_with_valid_email_sends_email(self, mock_send_mail):
        response = self.client.post(
            self.url, {"email": "user@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.data)
        mock_send_mail.assert_called_once()

    @patch("apps.authentication.serializers.send_mail")
    def test_request_with_invalid_email_returns_200(self, mock_send_mail):
        response = self.client.post(
            self.url, {"email": "nobody@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        mock_send_mail.assert_not_called()

    @patch("apps.authentication.serializers.send_mail")
    def test_request_with_inactive_user_returns_200_no_email(self, mock_send_mail):
        User.objects.create_user(
            email="inactive@example.com",
            password=self.password,
            first_name="Inactive",
            last_name="User",
            is_active=False,
        )
        response = self.client.post(
            self.url, {"email": "inactive@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        mock_send_mail.assert_not_called()

    def test_request_with_missing_email_returns_400(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_request_with_invalid_email_format_returns_400(self):
        response = self.client.post(
            self.url, {"email": "not-an-email"}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    @patch("apps.authentication.serializers.send_mail")
    def test_request_with_uppercase_email_still_finds_user(self, mock_send_mail):
        response = self.client.post(
            self.url, {"email": "USER@EXAMPLE.COM"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        mock_send_mail.assert_called_once()

    def test_request_get_method_returns_405(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    @patch("apps.authentication.serializers.send_mail")
    def test_request_email_contains_reset_link(self, mock_send_mail):
        response = self.client.post(
            self.url, {"email": "user@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, 200)

        call_kwargs = mock_send_mail.call_args[1]
        html_body = call_kwargs.get("html_message", "")
        text_body = call_kwargs.get("message", "")
        self.assertIn("reset-password", text_body)
        self.assertIn("token=", text_body)


class PasswordResetConfirmTest(APITestCase):
    def setUp(self):
        self.url = "/api/v1/auth/password-reset/confirm/"
        self.password = "password123"
        self.new_password = "new-secure-password123"
        self.user = User.objects.create_user(
            email="user@example.com",
            password=self.password,
            first_name="Test",
            last_name="User",
        )
        self.token = token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(str(self.user.pk).encode())

    def test_confirm_with_valid_token(self):
        response = self.client.post(
            self.url,
            {"token": self.token, "email": "user@example.com", "password": self.new_password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))

    def test_confirm_with_invalid_token(self):
        response = self.client.post(
            self.url,
            {"token": "invalid-token", "email": "user@example.com", "password": self.new_password},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_confirm_with_expired_token(self):
        from datetime import timedelta
        from django.utils import timezone

        old_user = User.objects.create_user(
            email="old@example.com",
            password=self.password,
            first_name="Old",
            last_name="User",
        )
        old_token = token_generator.make_token(old_user)

        old_user.set_password("brand-new-password123")
        old_user.save()

        response = self.client.post(
            self.url,
            {"token": old_token, "email": "old@example.com", "password": self.new_password},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_confirm_with_wrong_email(self):
        response = self.client.post(
            self.url,
            {"token": self.token, "email": "wrong@example.com", "password": self.new_password},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_confirm_with_weak_password(self):
        response = self.client.post(
            self.url,
            {"token": self.token, "email": "user@example.com", "password": "123"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_confirm_old_token_invalid_after_password_change(self):
        response = self.client.post(
            self.url,
            {"token": self.token, "email": "user@example.com", "password": self.new_password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        response2 = self.client.post(
            self.url,
            {"token": self.token, "email": "user@example.com", "password": "another-password123"},
            format="json",
        )
        self.assertEqual(response2.status_code, 400)

    def test_confirm_with_missing_fields(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_confirm_get_method_returns_405(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class PasswordChangeTest(APITestCase):
    def setUp(self):
        self.url = "/api/v1/auth/password-change/"
        self.password = "password123"
        self.new_password = "new-secure-password123"
        self.user = User.objects.create_user(
            email="user@example.com",
            password=self.password,
            first_name="Test",
            last_name="User",
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def _auth_header(self):
        return f"Bearer {self.access_token}"

    def test_change_with_valid_passwords(self):
        response = self.client.post(
            self.url,
            {"current_password": self.password, "new_password": self.new_password},
            format="json",
            HTTP_AUTHORIZATION=self._auth_header(),
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))

    def test_change_with_wrong_current_password(self):
        response = self.client.post(
            self.url,
            {"current_password": "wrong-password", "new_password": self.new_password},
            format="json",
            HTTP_AUTHORIZATION=self._auth_header(),
        )
        self.assertEqual(response.status_code, 400)

    def test_change_with_weak_new_password(self):
        response = self.client.post(
            self.url,
            {"current_password": self.password, "new_password": "123"},
            format="json",
            HTTP_AUTHORIZATION=self._auth_header(),
        )
        self.assertEqual(response.status_code, 400)

    def test_change_without_auth_returns_403(self):
        response = self.client.post(
            self.url,
            {"current_password": self.password, "new_password": self.new_password},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_change_with_missing_fields(self):
        response = self.client.post(
            self.url, {}, format="json", HTTP_AUTHORIZATION=self._auth_header()
        )
        self.assertEqual(response.status_code, 400)

    def test_change_get_method_returns_405(self):
        response = self.client.get(self.url, HTTP_AUTHORIZATION=self._auth_header())
        self.assertEqual(response.status_code, 405)

    def test_change_password_then_login_with_new(self):
        response = self.client.post(
            self.url,
            {"current_password": self.password, "new_password": self.new_password},
            format="json",
            HTTP_AUTHORIZATION=self._auth_header(),
        )
        self.assertEqual(response.status_code, 200)

        login_response = self.client.post(
            "/api/v1/auth/login/",
            {"email": "user@example.com", "password": self.new_password},
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", login_response.data)

    def test_old_password_no_longer_works(self):
        response = self.client.post(
            self.url,
            {"current_password": self.password, "new_password": self.new_password},
            format="json",
            HTTP_AUTHORIZATION=self._auth_header(),
        )
        self.assertEqual(response.status_code, 200)

        login_response = self.client.post(
            "/api/v1/auth/login/",
            {"email": "user@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(login_response.status_code, 401)
