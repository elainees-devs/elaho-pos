from rest_framework import status, viewsets
from rest_framework.response import Response

from ..serializers import RolePermissionSerializer
from ..services.role_permission_service import RolePermissionService


class RolePermissionViewSet(viewsets.ViewSet):
    """
    ==================================================
    Role Permission ViewSet
    ==================================================

    Purpose:
    --------
    Handles HTTP requests for RolePermission resources.

    Responsibilities:
    -----------------
    - Receive HTTP requests.
    - Delegate validation to the serializer.
    - Delegate business logic to the service layer.
    - Return HTTP responses.

    Design Principle:
    -----------------
    Single Responsibility Principle (SRP)
    """

    def list(self, request):
        role_permissions = RolePermissionService.list_role_permissions()
        serializer = RolePermissionSerializer(role_permissions, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        role_permission = RolePermissionService.get_role_permission(pk)
        serializer = RolePermissionSerializer(role_permission)
        return Response(serializer.data)

    def create(self, request):
        serializer = RolePermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_permission = RolePermissionService.assign_permission(
            role=serializer.validated_data["role"],
            permission=serializer.validated_data["permission"],
        )

        return Response(
            RolePermissionSerializer(role_permission).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, pk=None):
        role_permission = RolePermissionService.get_role_permission(pk)

        serializer = RolePermissionSerializer(
            role_permission,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        role_permission = RolePermissionService.update_role_permission(
            role_permission,
            **serializer.validated_data,
        )

        return Response(RolePermissionSerializer(role_permission).data)

    def partial_update(self, request, pk=None):
        role_permission = RolePermissionService.get_role_permission(pk)

        serializer = RolePermissionSerializer(
            role_permission,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        role_permission = RolePermissionService.update_role_permission(
            role_permission,
            **serializer.validated_data,
        )

        return Response(RolePermissionSerializer(role_permission).data)

    def destroy(self, request, pk=None):
        role_permission = RolePermissionService.get_role_permission(pk)

        RolePermissionService.remove_permission(role_permission)

        return Response(status=status.HTTP_204_NO_CONTENT)