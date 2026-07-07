from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),

    # ------------------------------------------------------------------
    # Version 1 API Endpoints
    # ------------------------------------------------------------------

    path("api/v1/roles/", include("apps.roles.urls")),
    path("api/v1/users/", include("apps.users.urls")),
]