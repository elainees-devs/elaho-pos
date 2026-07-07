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
- Create and update Role instances.
- Define which model fields are exposed through the API.

Does NOT:
----------
- Contain business logic.
- Perform permission checks.
- Query unrelated models.
- Handle HTTP requests or responses.

Design Principle:
-----------------
Single Responsibility Principle (SRP)

This serializer is responsible only for translating
between Role model instances and API representations.
Business rules belong in services or models, while
request handling belongs in views.
"""

from rest_framework import serializers

from apps.roles.models import Role


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Role model.

    Converts Role model instances into JSON responses and
    validates incoming JSON data before creating or updating
    Role records.
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