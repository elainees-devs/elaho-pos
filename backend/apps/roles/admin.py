from django.contrib import admin
from .models import Role

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description","level", "is_active","created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("level","is_active",)