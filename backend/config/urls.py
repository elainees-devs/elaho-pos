from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from apps.authentication.views import LoginView


urlpatterns = [
    path("admin/", admin.site.urls),

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    path("api/v1/auth/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/auth/", include("apps.authentication.urls")),

    # ------------------------------------------------------------------
    # Version 1 API Endpoints
    # ------------------------------------------------------------------

    path("api/v1/roles/", include("apps.roles.urls")),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/businesses/", include("apps.businesses.urls")),
]