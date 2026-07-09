"""
==================================================
Role View
==================================================

Purpose:
--------
Handles HTTP requests for the Role API.

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

from rest_framework import status, viewsets
from rest_framework.response import Response

from ..serializers import RoleSerializer
from ..services.role_service import RoleService


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Role resources.
    """

    serializer_class = RoleSerializer

    def get_queryset(self):
        return RoleService.list_roles()

    def get_object(self):
        return RoleService.get_role(self.kwargs["pk"])

    def list(self, request, *args, **kwargs):
        roles = self.get_queryset()
        serializer = self.get_serializer(roles, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        role = self.get_object()
        serializer = self.get_serializer(role)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.save()

        return Response(
            self.get_serializer(role).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        role = self.get_object()

        serializer = self.get_serializer(
            role,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        role = serializer.save()

        return Response(
            self.get_serializer(role).data,
            status=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        role = self.get_object()

        serializer = self.get_serializer(
            role,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        role = serializer.save()

        return Response(
            self.get_serializer(role).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        role = self.get_object()

        RoleService.delete_role(role)

        return Response(
            {
                "message": "Role deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT,
        )

