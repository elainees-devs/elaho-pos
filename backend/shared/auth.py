from rest_framework_simplejwt.authentication import (
    JWTAuthentication as BaseJWTAuthentication,
)
from rest_framework.authentication import (
    SessionAuthentication as BaseSessionAuthentication,
)

from .permission import get_permission_codes


def _prefetch_user_permissions(user):
    get_permission_codes(user)


class JWTAuthentication(BaseJWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            user, token = result
            _prefetch_user_permissions(user)
        return result


class SessionAuthentication(BaseSessionAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            user, token = result
            _prefetch_user_permissions(user)
        return result
