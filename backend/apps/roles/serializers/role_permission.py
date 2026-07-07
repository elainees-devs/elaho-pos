from rest_framework import serializers

from ..models import RolePermission
class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for the RolePermission model.

    Converts RolePermission model instances into JSON responses and
    validates incoming JSON data before creating or updating
    RolePermission records.
    """
    class Meta:
        model = RolePermission
        fields = (
            "id",
            "role",
            "permission",
            "created_at",
            "updated_at"
            
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )