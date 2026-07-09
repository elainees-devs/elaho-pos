from rest_framework import serializers

from ..models import Permission
from ..services import PermissionService

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
    def create(self, validated_data):
        """
        Delegate permission creation to the service layer.
        """
        return PermissionService.create_permission(**validated_data)

    def update(self, instance, validated_data):
        """
        Delegate permission updates to the service layer.
        """
        return PermissionService.update_permission(
            role=instance,
            **validated_data,
        )