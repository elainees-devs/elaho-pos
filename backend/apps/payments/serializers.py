from rest_framework import serializers

from apps.subscriptions.models import SubscriptionPlan

from .models import (
    BillingCycle,
    Payment,
    PaymentAuditLog,
    PaymentMethod,
    PaymentStatus,
    RegistrationInvitation,
)


class PaymentListSerializer(serializers.ModelSerializer):
    subscription_plan_name = serializers.CharField(
        source="subscription_plan.name",
        read_only=True,
    )
    verified_by_name = serializers.SerializerMethodField()
    registration_status = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "uuid",
            "owner_name",
            "owner_email",
            "owner_phone",
            "business_name",
            "subscription_plan",
            "subscription_plan_name",
            "billing_cycle",
            "amount",
            "currency",
            "payment_method",
            "reference_number",
            "payment_date",
            "status",
            "verified_by",
            "verified_by_name",
            "verified_at",
            "registration_status",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "uuid",
            "status",
            "verified_at",
            "verified_by",
            "created_at",
            "updated_at",
        )

    def get_verified_by_name(self, obj):
        if obj.verified_by:
            return obj.verified_by.full_name
        return None

    def get_registration_status(self, obj):
        if hasattr(obj, "invitation"):
            invitation = obj.invitation
            if invitation.is_used:
                return "registered"
            return "pending_registration"
        return "no_invitation"


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "owner_name",
            "owner_email",
            "owner_phone",
            "business_name",
            "subscription_plan",
            "billing_cycle",
            "amount",
            "currency",
            "payment_method",
            "reference_number",
            "payment_date",
            "notes",
        )

    def validate_owner_email(self, value):
        return value.strip().lower()

    def validate_owner_name(self, value):
        return value.strip()

    def validate_business_name(self, value):
        return value.strip()

    def validate_reference_number(self, value):
        return value.strip() if value else value

    def validate(self, attrs):
        plan = attrs["subscription_plan"]
        cycle = attrs["billing_cycle"]

        if cycle == BillingCycle.MONTHLY:
            expected = plan.monthly_price
        else:
            expected = plan.annual_price

        if attrs["amount"] != expected:
            raise serializers.ValidationError(
                {
                    "amount": (
                        f"Amount must be {expected} for {plan.name} "
                        f"({cycle} billing)."
                    )
                }
            )

        return attrs


class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "owner_name",
            "owner_email",
            "owner_phone",
            "business_name",
            "subscription_plan",
            "billing_cycle",
            "amount",
            "currency",
            "payment_method",
            "reference_number",
            "payment_date",
            "notes",
        )

    def validate_owner_email(self, value):
        return value.strip().lower()

    def validate_owner_name(self, value):
        return value.strip()

    def validate_business_name(self, value):
        return value.strip()

    def validate_reference_number(self, value):
        return value.strip() if value else value


class PaymentCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional reason for cancellation.",
    )


class PaymentRefundSerializer(serializers.Serializer):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional reason for refund.",
    )


class PaymentAuditLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PaymentAuditLog
        fields = (
            "id",
            "payment",
            "action",
            "performed_by",
            "performed_by_name",
            "description",
            "timestamp",
        )
        read_only_fields = fields

    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return obj.performed_by.full_name
        return None


class RegistrationInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationInvitation
        fields = (
            "id",
            "payment",
            "email",
            "owner_name",
            "business_name",
            "is_used",
            "expires_at",
            "created_by",
            "created_at",
        )
        read_only_fields = fields


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "monthly_price",
            "annual_price",
            "max_users",
            "max_branches",
            "max_products",
            "is_active",
        )
        read_only_fields = ("id",)


class PaymentDashboardSerializer(serializers.Serializer):
    total_payments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    verified_payments = serializers.IntegerField()
    active_subscriptions = serializers.IntegerField()
    monthly_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    expired_subscriptions = serializers.IntegerField()
