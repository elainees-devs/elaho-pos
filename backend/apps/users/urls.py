from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import InviteUserView, UserViewSet

router = DefaultRouter()
router.register("", UserViewSet, basename="users")

urlpatterns = router.urls + [
    path("invite/", InviteUserView.as_view(), name="invite_user"),
]