from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.roles.models import Role
from apps.users.serializers import UserSerializer


User = get_user_model()


class UserSerializerTest(TestCase):
    """
    Tests for UserSerializer.
    """

    def test_user_serializer(self):

        user = User.objects.create_user(
            email="jane@example.com",
            password="password123",
            first_name="Jane",
            last_name="Smith",
            phone="0722222222",
        )

        serializer = UserSerializer(user)

        self.assertEqual(
            serializer.data["email"],
            "jane@example.com",
        )

        self.assertEqual(
            serializer.data["first_name"],
            "Jane",
        )

        self.assertEqual(
            serializer.data["last_name"],
            "Smith",
        )

        self.assertEqual(
            serializer.data["phone"],
            "0722222222",
        )

        self.assertTrue(
            serializer.data["is_active"],
        )

        self.assertFalse(
            serializer.data["is_deleted"],
        )


    def test_user_serializer_with_role(self):

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

        serializer = UserSerializer(user)

        self.assertEqual(
            serializer.data["role"],
            role.id,
        )


    def test_user_serializer_read_only_fields(self):

        user = User.objects.create_user(
            email="readonly@example.com",
            password="password123",
            first_name="Read",
            last_name="Only",
        )

        serializer = UserSerializer(user)

        self.assertIn(
            "id",
            serializer.data,
        )

        self.assertIn(
            "created_at",
            serializer.data,
        )

        self.assertIn(
            "updated_at",
            serializer.data,
        )