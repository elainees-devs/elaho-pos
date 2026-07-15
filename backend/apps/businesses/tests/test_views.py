from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.businesses.models import Business

User = get_user_model()


class BusinessModelTest(APITestCase):
    """Tests for the Business model."""

    def test_slug_auto_generated(self):
        b = Business.objects.create(name="Mama Njeri Shop")
        self.assertEqual(b.slug, "mama-njeri-shop")

    def test_slug_collision_appends_suffix(self):
        b1 = Business.objects.create(name="Test Shop")
        b2 = Business.objects.create(name="Test Shop")
        self.assertNotEqual(b1.slug, b2.slug)
        self.assertTrue(b2.slug.startswith("test-shop-"))

    def test_str(self):
        b = Business.objects.create(name="My Shop")
        self.assertEqual(str(b), "My Shop")

    def test_owner_nullable(self):
        b = Business.objects.create(name="No Owner Shop")
        self.assertIsNone(b.owner)

    def test_defaults(self):
        b = Business.objects.create(name="Defaults Shop")
        self.assertTrue(b.is_active)
        self.assertFalse(b.is_deleted)


class BusinessViewSetTest(APITestCase):
    """Tests for POST /api/v1/businesses/ and GET /api/v1/businesses/"""

    def setUp(self):
        self.url = "/api/v1/businesses/"
        self.superadmin = User.objects.create_superuser(
            email="admin@example.com",
            password="admin1234",
            first_name="Admin",
            last_name="User",
        )
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            first_name="Normal",
            last_name="User",
        )
        refresh = RefreshToken.for_user(self.superadmin)
        self.admin_token = str(refresh.access_token)
        refresh = RefreshToken.for_user(self.normal_user)
        self.user_token = str(refresh.access_token)

    def _admin_header(self):
        return f"Bearer {self.admin_token}"

    def _user_header(self):
        return f"Bearer {self.user_token}"

    def test_create_business_as_superadmin(self):
        response = self.client.post(
            self.url,
            {"name": "Mama Njeri Shop"},
            format="json",
            HTTP_AUTHORIZATION=self._admin_header(),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Mama Njeri Shop")
        self.assertEqual(response.data["slug"], "mama-njeri-shop")

    def test_create_business_normal_user_forbidden(self):
        response = self.client.post(
            self.url,
            {"name": "Should Fail"},
            format="json",
            HTTP_AUTHORIZATION=self._user_header(),
        )
        self.assertEqual(response.status_code, 403)

    def test_create_business_unauthenticated(self):
        response = self.client.post(
            self.url,
            {"name": "Should Fail"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_create_business_missing_name(self):
        response = self.client.post(
            self.url,
            {},
            format="json",
            HTTP_AUTHORIZATION=self._admin_header(),
        )
        self.assertEqual(response.status_code, 400)

    def test_list_businesses(self):
        Business.objects.create(name="Shop One")
        Business.objects.create(name="Shop Two")
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=self._admin_header(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_businesses_search(self):
        Business.objects.create(name="Mama Njeri Shop")
        Business.objects.create(name="Mama Njeri Hardware")
        Business.objects.create(name="Different Shop")
        response = self.client.get(
            self.url,
            {"q": "Mama"},
            HTTP_AUTHORIZATION=self._admin_header(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_create_business_with_optional_fields(self):
        response = self.client.post(
            self.url,
            {
                "name": "Full Shop",
                "phone": "0711111111",
                "email": "shop@example.com",
                "address": "Nairobi, Kenya",
                "kra_pin": "A123456789B",
            },
            format="json",
            HTTP_AUTHORIZATION=self._admin_header(),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["phone"], "0711111111")
        self.assertEqual(response.data["kra_pin"], "A123456789B")

    def test_create_business_kra_pin_optional(self):
        response = self.client.post(
            self.url,
            {"name": "No PIN Shop"},
            format="json",
            HTTP_AUTHORIZATION=self._admin_header(),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["kra_pin"], "")

    def test_get_returns_405(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=self._admin_header(),
        )
        self.assertEqual(response.status_code, 200)
