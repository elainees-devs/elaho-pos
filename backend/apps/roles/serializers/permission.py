from rest_framework import serializers

from roles.models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Permission model.

    Converts Permission model instances into JSON responses and
    validates incoming JSON data before creating or updating
    Permission records.
    """
    class Meta:
        model = Permission
        fields = (
            "id",
            "name",
            "code",
            "description",
            "created_at",
            "updated_at"
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )