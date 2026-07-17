from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.serializers import InviteUserSerializer
from shared.constants import PermissionCode
from shared.permission import HasPermission, IsSuperAdmin

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing User resources.

    Provides the following REST API operations:

    - GET    /users/          List all users (business-scoped)
    - GET    /users/{id}/     Retrieve a specific user
    - POST   /users/          Create a new user (auto-sets business FK)
    - PUT    /users/{id}/     Replace an existing user details
    - PATCH  /users/{id}/     Partially update user details
    - DELETE /users/{id}/     Delete a user
    """

    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(business=user.business)

    def get_permissions(self):
        permissions = super().get_permissions()
        if self.action in ("list", "retrieve"):
            permissions.append(HasPermission(PermissionCode.USER_VIEW)())
        elif self.action == "create":
            permissions.append(HasPermission(PermissionCode.USER_CREATE)())
        elif self.action in ("update", "partial_update"):
            permissions.append(HasPermission(PermissionCode.USER_UPDATE)())
        elif self.action == "destroy":
            permissions.append(HasPermission(PermissionCode.USER_DELETE)())
        return permissions


class InviteUserView(APIView):
    """
    POST /api/v1/users/invite/

    Sends an email invitation to a new user so they can self-register.
    Requires USER_CREATE permission. Scoped to the requester's business.
    """

    permission_classes = [IsAuthenticated, HasPermission(PermissionCode.USER_CREATE)]

    def post(self, request):
        serializer = InviteUserSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(
            {"detail": "Invitation sent successfully."},
            status=status.HTTP_200_OK,
        )