from django.contrib import admin
from .models import SubscriptionPlan, Subscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "monthly_price",
        "annual_price",
        "max_users",
        "max_branches",
        "max_products",
        "is_active",
    )
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "business",
        "plan",
        "billing_cycle",
        "amount",
        "start_date",
        "end_date",
        "status",
        "auto_renew",
    )
    list_filter = ("status", "billing_cycle", "auto_renew")
    search_fields = ("business__name",)
    raw_id_fields = ("business", "payment", "plan")
