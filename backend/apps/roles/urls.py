from rest_framework.routers import DefaultRouter

from .views import (
    RoleViewSet,
    PermissionViewSet,
    RolePermissionViewSet,
)


router = DefaultRouter()

router.register(
    r"permissions",
    PermissionViewSet,
    basename="permission"
)

router.register(
    r"role-permissions",
    RolePermissionViewSet,
    basename="role-permission"
)

router.register(
    r"",
    RoleViewSet,
    basename="role"
)


urlpatterns = router.urls