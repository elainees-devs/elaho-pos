from rest_framework import viewsets

from ..models import RolePermission
from ..serializers import RolePermissionSerializer


class RolePermissionViewSet(viewsets.ModelViewSet):
    """
ViewSet for managing RolePermission resources.

Provides the following REST API operations:

- GET    /role-permissions/          List all role permissions
- GET    /role-permissions/{id}/     Retrieve a specific role permission assignment
- POST   /role-permissions/          Create a new role permission assignment
- PUT    /role-permissions/{id}/     Replace an existing role permission assignment
- PATCH  /role-permissions/{id}/     Partially update a role permission assignment
- DELETE /role-permissions/{id}/     Delete a role permission assignment
"""
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer