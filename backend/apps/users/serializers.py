from rest_framework import serializers

from apps.users.models import UserModel
class UserSerializer(serializers.ModelUser):
    model = UserModel
    class Meta:
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "is_active",
            "created_at",
            "updated_at"
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at"
        )
