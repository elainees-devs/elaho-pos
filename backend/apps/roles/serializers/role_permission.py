from rest_framework import serializers

from ..models import RolePermission


class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for the RolePermission model.

    Responsibilities:
    -----------------
    - Convert RolePermission model instances to JSON.
    - Validate incoming request data.
    - Prevent duplicate role-permission mappings.

    Business logic such as assigning or removing permissions
    belongs in the RolePermissionService.
    """

    class Meta:
        model = RolePermission
        fields = (
            "id",
            "role",
            "permission",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        """
        Ensure a role cannot be assigned the same permission twice.
        """

        role = attrs.get("role")
        permission = attrs.get("permission")

        queryset = RolePermission.objects.filter(
            role=role,
            permission=permission,
        )

        # Exclude current instance during updates
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "This permission is already assigned to the selected role."
                    ]
                }
            )

        return attrs