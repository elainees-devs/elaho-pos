from django.apps import AppConfig


class RolesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.roles"
    label = "roles"

    def ready(self):
        from . import signals  # noqa: F401
