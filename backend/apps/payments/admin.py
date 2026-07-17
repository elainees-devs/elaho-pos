from django.contrib import admin
from .models import Payment, RegistrationInvitation, PaymentAuditLog


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "owner_name",
        "subscription_plan",
        "amount",
        "currency",
        "payment_method",
        "status",
        "created_at",
    )
    list_filter = ("status", "payment_method", "billing_cycle", "created_at")
    search_fields = (
        "business_name",
        "owner_name",
        "owner_email",
        "reference_number",
    )
    readonly_fields = (
        "uuid",
        "verified_at",
        "verified_by",
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("subscription_plan", "verified_by")


@admin.register(RegistrationInvitation)
class RegistrationInvitationAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "email",
        "is_used",
        "expires_at",
        "created_at",
    )
    list_filter = ("is_used", "created_at")
    search_fields = ("business_name", "email", "owner_name")
    readonly_fields = ("token_hash", "created_at")
    raw_id_fields = ("payment", "created_by")


@admin.register(PaymentAuditLog)
class PaymentAuditLogAdmin(admin.ModelAdmin):
    list_display = ("payment", "action", "performed_by", "timestamp")
    list_filter = ("action", "timestamp")
    readonly_fields = (
        "payment",
        "action",
        "performed_by",
        "description",
        "timestamp",
    )
    raw_id_fields = ("payment", "performed_by")
