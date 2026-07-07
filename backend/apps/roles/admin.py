from django.contrib import admin
from .models import Role

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)
