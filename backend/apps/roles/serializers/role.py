"""
==================================================
Role Serializer
==================================================

Purpose:
--------
Converts Role model instances to and from JSON for
the REST API.

Responsibilities:
-----------------
- Serialize Role objects into JSON responses.
- Validate incoming Role data.
- Delegate create and update operations to RoleService.
- Define which model fields are exposed through the API.

Does NOT:
----------
- Contain business logic.
- Perform permission checks.
- Handle HTTP requests or responses.

Design Principle:
-----------------
Single Responsibility Principle (SRP)

This serializer is responsible only for translating
between Role model instances and API representations.
Business rules belong in the service layer.
"""

from rest_framework import serializers

from ..models import Role
from ..services.role_service import RoleService


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Role model.
    """

    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "description",
            "level",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        """
        Delegate role creation to the service layer.
        """
        return RoleService.create_role(**validated_data)

    def update(self, instance, validated_data):
        """
        Delegate role updates to the service layer.
        """
        return RoleService.update_role(
            role=instance,
            **validated_data,
        )
    
