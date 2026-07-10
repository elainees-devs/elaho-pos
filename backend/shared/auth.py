from django.core.cache import cache
from rest_framework_simplejwt.authentication import (
    JWTAuthentication as BaseJWTAuthentication,
)
from rest_framework.authentication import (
    SessionAuthentication as BaseSessionAuthentication,
)


def _prefetch_user_permissions(user):
    role = getattr(user, "role", None)
    if role is None:
        return

    cache_key = f"perm_codes_{role.pk}"
    if cache.get(cache_key) is not None:
        return

    codes = frozenset(
        role.permissions.values_list("permission__code", flat=True)
    )
    cache.set(cache_key, codes, timeout=300)


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
