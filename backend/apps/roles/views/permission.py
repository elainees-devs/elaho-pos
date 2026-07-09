from rest_framework import status, viewsets
from rest_framework.response import Response

from ..serializers import PermissionSerializer
from ..services.permission_service import PermissionService


class PermissionViewSet(viewsets.ViewSet):
    """
    ==================================================
    Permission View
    ==================================================

    Purpose:
    --------
    Handles HTTP requests for the Permission API.

    Responsibilities:
    -----------------
    - Receive HTTP requests.
    - Delegate validation to the serializer.
    - Delegate business logic to the service layer.
    - Return HTTP responses with appropriate status codes.

    Design Principle:
    -----------------
    Single Responsibility Principle (SRP)
    """

    service = PermissionService()

    def list(self, request):
        """Return a paginated list of permissions."""
        permissions = self.service.list_permissions()

        page = self.paginate_queryset(permissions)
        if page is not None:
            serializer = PermissionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Return a single permission by ID."""
        permission = self.service.get_permission(pk)
        serializer = PermissionSerializer(permission)
        return Response(serializer.data)

    def create(self, request):
        """Create a new permission."""
        serializer = PermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        permission = self.service.create_permission(serializer.validated_data)

        return Response(
            PermissionSerializer(permission).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, pk=None):
        """Replace an existing permission."""
        serializer = PermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        permission = self.service.update_permission(pk, serializer.validated_data)

        return Response(PermissionSerializer(permission).data)

    def partial_update(self, request, pk=None):
        """Partially update an existing permission."""
        serializer = PermissionSerializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        permission = self.service.update_permission(pk, serializer.validated_data)

        return Response(PermissionSerializer(permission).data)

    def destroy(self, request, pk=None):
        """Delete a permission."""
        self.service.delete_permission(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)