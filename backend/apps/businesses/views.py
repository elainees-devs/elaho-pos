from rest_framework import viewsets

from shared.permission import IsSuperAdmin

from .models import Business
from .serializers import BusinessSerializer


class BusinessViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Business resources.

    - GET    /businesses/          List all businesses (search by name)
    - GET    /businesses/{id}/     Retrieve a specific business
    - POST   /businesses/          Create a new business (superadmin only)
    - PUT    /businesses/{id}/     Replace business details
    - PATCH  /businesses/{id}/     Partially update business details
    - DELETE /businesses/{id}/     Soft-delete a business
    """

    queryset = Business.objects.filter(is_deleted=False)
    serializer_class = BusinessSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsSuperAdmin()]
        if self.action in ("update", "partial_update"):
            return [IsSuperAdmin()]
        if self.action == "destroy":
            return [IsSuperAdmin()]
        return [IsSuperAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(name__icontains=q)
        return qs
