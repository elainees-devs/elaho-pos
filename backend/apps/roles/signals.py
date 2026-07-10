from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models.role_permission import RolePermission


@receiver([post_save, post_delete], sender=RolePermission)
def invalidate_role_perm_cache(sender, instance, **kwargs):
    cache_key = f"perm_codes_{instance.role_id}"
    cache.delete(cache_key)
