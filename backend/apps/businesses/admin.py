from django.contrib import admin

from .models import Business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "owner",
        "phone",
        "kra_pin",
        "is_active",
        "is_deleted",
        "created_at",
    )
    list_filter = ("is_active", "is_deleted")
    search_fields = ("name", "slug", "owner__email")
    readonly_fields = ("slug", "created_at", "updated_at")
