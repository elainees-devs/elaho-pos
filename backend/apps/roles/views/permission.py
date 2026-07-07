from rest_framework import viewsets

from ..models import Permission
from ..serializers import PermissionSerializer

class PermissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Permission resources.

    Provides the following REST API operations:

    - GET    /permissions/          List all permissions
    - GET    /permissions/{id}/     Retrieve a specific permission
    - POST   /permissions/          Create a new permission
    - PUT    /permissions/{id}/     Replace an existing permission
    - PATCH  /permissions/{id}/     Partially update a permission
    - DELETE /permissions/{id}/     Delete a permission
    """
    class Meta:
        queryset = Permission.object.all()
        serializer_class = PermissionSerializer
