from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.businesses.models import Business

User = get_user_model()


class RegisterBusinessViewTest(APITestCase):
    def setUp(self):
        self.url = "/api/v1/auth/register-business/"
        self.payload = {
            "business_name": "Northwind Traders",
            "business_phone": "+254700000000",
            "business_email": "shop@example.com",
            "business_address": "Nairobi",
            "kra_pin": "A123456789B",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "owner@example.com",
            "phone": "+254711111111",
            "password": "NorthwindOwner991!",
        }
        self.superadmin = User.objects.create_superuser(
            email="admin@example.com",
            password="Adminpass1",
            first_name="Admin",
            last_name="User",
        )
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="Userpass1",
            first_name="Normal",
            last_name="User",
        )

    def _auth_header_for(self, user):
        refresh = RefreshToken.for_user(user)
        return f"Bearer {refresh.access_token}"

    def test_unauthenticated_request_is_forbidden(self):
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Business.objects.filter(name="Northwind Traders").exists())

    def test_normal_user_request_is_forbidden(self):
        response = self.client.post(
            self.url,
            self.payload,
            format="json",
            HTTP_AUTHORIZATION=self._auth_header_for(self.normal_user),
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Business.objects.filter(name="Northwind Traders").exists())

    def test_superadmin_can_create_business_and_owner(self):
        response = self.client.post(
            self.url,
            self.payload,
            format="json",
            HTTP_AUTHORIZATION=self._auth_header_for(self.superadmin),
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        business = Business.objects.get(name="Northwind Traders")
        owner = User.objects.get(email="owner@example.com")
        self.assertEqual(business.owner, owner)
        self.assertEqual(owner.business, business)