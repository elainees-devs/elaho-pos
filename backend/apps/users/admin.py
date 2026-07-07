from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "role",
        "is_active",
        "date_joined",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("is_active", "role", "is_deleted")
