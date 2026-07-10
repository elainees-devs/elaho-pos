from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.roles.models import Role, Permission, RolePermission
from shared.constants import PermissionCode

from .factories import PermissionFactory, RoleFactory, RolePermissionFactory

User = get_user_model()


class JWTLoginTest(APITestCase):
    def setUp(self):
        self.url = "/api/v1/auth/login/"
        self.password = "password123"
        self.role = RoleFactory(name="Staff", level=10)
        self.user = User.objects.create_user(
            email="staff@example.com",
            password=self.password,
            first_name="Staff",
            last_name="User",
            role=self.role,
        )

    def test_login_with_valid_credentials_returns_tokens(self):
        response = self.client.post(
            self.url,
            {"email": "staff@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_wrong_password_returns_401(self):
        response = self.client.post(
            self.url,
            {"email": "staff@example.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_login_with_nonexistent_email_returns_401(self):
        response = self.client.post(
            self.url,
            {"email": "nobody@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_login_with_inactive_user_returns_401(self):
        User.objects.create_user(
            email="inactive@example.com",
            password=self.password,
            first_name="Inactive",
            last_name="User",
            is_active=False,
        )
        response = self.client.post(
            self.url,
            {"email": "inactive@example.com", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_login_with_missing_fields_returns_400(self):
        response = self.client.post(
            self.url,
            {"email": "staff@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_with_empty_body_returns_400(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_login_get_method_returns_405(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class JWTRefreshTest(APITestCase):
    def setUp(self):
        self.url = "/api/v1/auth/refresh/"
        self.password = "password123"
        self.user = User.objects.create_user(
            email="user@example.com",
            password=self.password,
            first_name="Refresh",
            last_name="User",
        )

    def _get_refresh_token(self):
        return str(RefreshToken.for_user(self.user))

    def test_refresh_with_valid_token_returns_new_access(self):
        refresh = self._get_refresh_token()
        response = self.client.post(
            self.url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_refresh_with_invalid_token_returns_401(self):
        response = self.client.post(
            self.url,
            {"refresh": "invalid.token.here"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_refresh_with_missing_field_returns_400(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_refresh_with_expired_token_returns_401(self):
        from datetime import timedelta
        from django.utils import timezone

        token = RefreshToken.for_user(self.user)
        token.set_exp(lifetime=timedelta(seconds=-1))
        token["exp"] = timezone.now() - timedelta(seconds=1)

        response = self.client.post(
            self.url,
            {"refresh": str(token)},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_refresh_get_method_returns_405(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class JWTProtectedEndpointTest(APITestCase):
    def setUp(self):
        self.password = "password123"
        self.role = RoleFactory(name="Manager", level=50)
        self.perm = PermissionFactory(code=PermissionCode.ROLE_VIEW.value)
        RolePermissionFactory(role=self.role, permission=self.perm)

        self.user = User.objects.create_user(
            email="manager@example.com",
            password=self.password,
            first_name="Manager",
            last_name="User",
            role=self.role,
        )

        self.list_url = "/api/v1/roles/"

    def _get_access_token(self):
        return str(RefreshToken.for_user(self.user).access_token)

    def test_valid_jwt_grants_access(self):
        token = self._get_access_token()
        response = self.client.get(
            self.list_url,
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_missing_auth_header_returns_403(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 403)

    def test_invalid_jwt_returns_403(self):
        response = self.client.get(
            self.list_url,
            HTTP_AUTHORIZATION="Bearer invalid.jwt.here",
        )
        self.assertEqual(response.status_code, 403)

    def test_expired_jwt_returns_403(self):
        from datetime import timedelta
        from django.utils import timezone

        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token
        access.set_exp(lifetime=timedelta(seconds=-1))
        access["exp"] = timezone.now() - timedelta(seconds=1)

        response = self.client.get(
            self.list_url,
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(response.status_code, 403)

    def test_jwt_with_wrong_token_type_returns_403(self):
        token = str(RefreshToken.for_user(self.user))
        response = self.client.get(
            self.list_url,
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_login_then_access_with_returned_token(self):
        login_resp = self.client.post(
            "/api/v1/auth/login/",
            {"email": "manager@example.com", "password": self.password},
            format="json",
        )
        access = login_resp.data["access"]

        response = self.client.get(
            self.list_url,
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(response.status_code, 200)
