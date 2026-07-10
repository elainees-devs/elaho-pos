from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from shared.constants import PERM_CACHE_PREFIX
from .models.role_permission import RolePermission


@receiver([post_save, post_delete], sender=RolePermission)
def invalidate_role_perm_cache(sender, instance, **kwargs):
    cache.delete(f"{PERM_CACHE_PREFIX}{instance.role_id}")
