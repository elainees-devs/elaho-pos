from django.db import models

from .role import Role
from .permission import Permission

class RolePermission(models.Model):
    role = models.ForeignKey(
        Role,
        on_delete = models.CASCADE,
        related_name = "permissions"
    )

    permission = models.ForeignKey(
        Permission,
        on_delete = models.CASCADE,
        related_name = "roles"
    )

    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = (
            "role",
            "permission"
        )