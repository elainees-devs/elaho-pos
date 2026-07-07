from django.contrib import admin
from .models import Role, Permission

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description","level", "is_active","created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("level","is_active",)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name","code", "description","is_active")
    search_fields = ("name","code")
    list_filter = ("is_active",)
