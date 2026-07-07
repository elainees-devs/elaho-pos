"""
==================================================
Role View
==================================================

Purpose:
--------
Handles HTTP requests for the Role API.

Responsibilities:
-----------------
- Receive HTTP requests from API clients.
- Retrieve Role records from the database.
- Pass Role model instances to the serializer.
- Return serialized JSON responses.
- Create new Role records.
- Update existing Role records.
- Delete Role records.

Does NOT:
----------
- Contain business logic.
- Perform complex data validation.
- Serialize or deserialize data.
- Manage database schema.

Design Principle:
-----------------
Single Responsibility Principle (SRP)

This view is responsible only for coordinating HTTP
requests and responses. It delegates data validation
and JSON conversion to the serializer, while business
rules belong in services or models.
"""
from rest_framework import viewsets

from ..models import Role
from ..serializers import RoleSerializer

class RoleViewSet(viewsets.ModelViewSet):
         """
    ViewSet for managing Role resources.

    Provides the following REST API operations:

    - GET    /roles/          List all roles
    - GET    /roles/{id}/     Retrieve a specific role
    - POST   /roles/          Create a new role
    - PUT    /roles/{id}/     Replace an existing role
    - PATCH  /roles/{id}/     Partially update a role
    - DELETE /roles/{id}/     Delete a role
    """
         queryset = Role.objects.all()
         serializer_class = RoleSerializer
