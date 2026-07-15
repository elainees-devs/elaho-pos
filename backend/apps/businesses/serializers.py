from rest_framework import serializers

from .models import Business


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = (
            "id",
            "name",
            "slug",
            "owner",
            "phone",
            "email",
            "address",
            "kra_pin",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "slug",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):
        return value.strip()

    def validate_email(self, value):
        if value:
            return value.strip().lower()
        return value
