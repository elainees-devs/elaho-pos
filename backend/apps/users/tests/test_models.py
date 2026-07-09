from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.roles.models import Role


User = get_user_model()


class UserModelTest(TestCase):
    """
    Tests for the custom User model.
    """

    def test_create_user_with_email_authentication(self):

        user = User.objects.create_user(
            email="john@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
        )

        self.assertEqual(
            user.email,
            "john@example.com"
        )

        self.assertTrue(
            user.check_password("password123")
        )

        self.assertTrue(
            user.is_active
        )

        self.assertFalse(
            user.is_deleted
        )


    def test_username_field_is_removed(self):

        user = User.objects.create_user(
            email="jane@example.com",
            password="password123",
            first_name="Jane",
            last_name="Smith",
        )

        self.assertIsNone(
            user.username
        )


    def test_email_is_normalized(self):

        user = User.objects.create_user(
            email="JOHN@EXAMPLE.COM",
            password="password123",
            first_name=" john ",
            last_name=" doe ",
        )

        self.assertEqual(
            user.email,
            "john@example.com"
        )

        self.assertEqual(
            user.first_name,
            "John"
        )

        self.assertEqual(
            user.last_name,
            "Doe"
        )

    def test_user_full_name_property(self):

        user = User.objects.create_user(
            email="mary@example.com",
            password="password123",
            first_name="Mary",
            last_name="Jones",
        )

        self.assertEqual(
            user.full_name,
            "Mary Jones"
        )


    def test_created_at_property_returns_date_joined(self):

        user = User.objects.create_user(
            email="alex@example.com",
            password="password123",
            first_name="Alex",
            last_name="Brown",
        )

        self.assertEqual(
            user.created_at,
            user.date_joined
        )


    def test_string_representation(self):

        user = User.objects.create_user(
            email="sam@example.com",
            password="password123",
            first_name="Sam",
            last_name="Wilson",
        )

        self.assertEqual(
            str(user),
            "Sam Wilson"
        )


    def test_user_can_have_role(self):

        role = Role.objects.create(
            name="Manager",
            level=50,
        )

        user = User.objects.create_user(
            email="manager@example.com",
            password="password123",
            first_name="Manager",
            last_name="User",
            role=role,
        )

        self.assertEqual(
            user.role,
            role
        )