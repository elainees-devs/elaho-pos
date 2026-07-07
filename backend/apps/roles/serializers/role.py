from rest_framework import serializers
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

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = "Role"
        fields = "__all__"

