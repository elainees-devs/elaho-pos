from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name","email","phone", "role","is_active","created_at" ,"updated_at", "is_deleted_at")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("is_active","role")
