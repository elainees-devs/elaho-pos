import logging

from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subscriptions.models import Subscription, SubscriptionStatus
from shared.permission import IsSuperAdmin

from .models import (
    Payment,
    PaymentAuditLog,
    PaymentStatus,
    RegistrationInvitation,
)
from .registration_serializers import (
    RegisterBusinessFromPaymentSerializer,
    ValidateRegistrationTokenSerializer,
)
from .serializers import (
    PaymentAuditLogSerializer,
    PaymentCancelSerializer,
    PaymentCreateSerializer,
    PaymentDashboardSerializer,
    PaymentListSerializer,
    PaymentRefundSerializer,
    PaymentUpdateSerializer,
    RegistrationInvitationSerializer,
    SubscriptionPlanSerializer,
)
from .services.payment_service import PaymentService

audit_logger = logging.getLogger("audit")


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Payment records.

    Only accessible by Super Admins.

    - GET    /payments/              List all payments
    - GET    /payments/{id}/         Retrieve a specific payment
    - POST   /payments/              Create a new payment record
    - PATCH  /payments/{id}/         Partially update a payment
    - DELETE /payments/{id}/         Delete a payment
    """

    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        qs = Payment.objects.select_related(
            "subscription_plan",
            "verified_by",
        ).prefetch_related("invitation")

        # Filter by status
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        # Search by business name or owner name/email
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(business_name__icontains=q)
                | Q(owner_name__icontains=q)
                | Q(owner_email__icontains=q)
            )

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "create":
            return PaymentCreateSerializer
        if self.action in ("update", "partial_update"):
            return PaymentUpdateSerializer
        return PaymentListSerializer

    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, pk=None):
        """
        POST /payments/{id}/verify/

        Verify a pending payment and send registration invitation.
        """
        payment = self.get_object()

        try:
            payment = PaymentService.verify_payment(
                payment=payment,
                verified_by=request.user,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        audit_logger.info(
            "payment_verified payment_id=%s verified_by=%s ip=%s",
            payment.pk,
            request.user.pk,
            request.META.get("REMOTE_ADDR", ""),
        )

        return Response(
            {"detail": "Payment verified successfully. Registration invitation sent."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """
        POST /payments/{id}/cancel/

        Cancel a payment.
        """
        payment = self.get_object()
        serializer = PaymentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment = PaymentService.cancel_payment(
                payment=payment,
                cancelled_by=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Payment cancelled successfully."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="refund")
    def refund(self, request, pk=None):
        """
        POST /payments/{id}/refund/

        Refund a paid payment.
        """
        payment = self.get_object()
        serializer = PaymentRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment = PaymentService.refund_payment(
                payment=payment,
                refunded_by=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Payment refunded successfully."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="resend-invitation")
    def resend_invitation(self, request, pk=None):
        """
        POST /payments/{id}/resend-invitation/

        Resend the registration invitation for a verified payment.
        """
        payment = self.get_object()

        try:
            invitation = PaymentService.resend_invitation(
                payment=payment,
                resent_by=request.user,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "Registration invitation resent successfully.",
                "expires_at": invitation.expires_at,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="audit-log")
    def audit_log(self, request, pk=None):
        """
        GET /payments/{id}/audit-log/

        Retrieve the audit log for a specific payment.
        """
        payment = self.get_object()
        logs = PaymentAuditLog.objects.filter(payment=payment).select_related(
            "performed_by"
        )
        serializer = PaymentAuditLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentDashboardView(APIView):
    """
    GET /payments/dashboard/

    Returns dashboard metrics for the payments module.
    """

    permission_classes = [IsSuperAdmin]

    def get(self, request):
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_payments = Payment.objects.count()
        pending_payments = Payment.objects.filter(status=PaymentStatus.PENDING).count()
        verified_payments = Payment.objects.filter(status=PaymentStatus.PAID).count()

        active_subscriptions = Subscription.objects.filter(
            status=SubscriptionStatus.ACTIVE,
            start_date__lte=now.date(),
            end_date__gte=now.date(),
        ).count()

        expired_subscriptions = Subscription.objects.filter(
            status=SubscriptionStatus.ACTIVE,
            end_date__lt=now.date(),
        ).count()

        monthly_revenue = Payment.objects.filter(
            status=PaymentStatus.PAID,
            verified_at__gte=current_month_start,
        ).aggregate(total=Sum("amount"))["total"] or 0

        return Response(
            {
                "total_payments": total_payments,
                "pending_payments": pending_payments,
                "verified_payments": verified_payments,
                "active_subscriptions": active_subscriptions,
                "monthly_revenue": str(monthly_revenue),
                "expired_subscriptions": expired_subscriptions,
            },
            status=status.HTTP_200_OK,
        )


class SubscriptionPlanListView(APIView):
    """
    GET /subscription-plans/

    List all active subscription plans.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.subscriptions.models import SubscriptionPlan
        plans = SubscriptionPlan.objects.filter(is_active=True)
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ValidateRegistrationTokenView(APIView):
    """
    GET /registration-invitations/{token}/

    Validates a registration invitation token and returns prefill data.
    """

    permission_classes = [AllowAny]

    def get(self, request, token):
        serializer = ValidateRegistrationTokenSerializer(data={"token": token})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        invitation = serializer.validated_data["invitation"]
        return Response(
            {
                "email": invitation.email,
                "owner_name": invitation.owner_name,
                "business_name": invitation.business_name,
                "subscription_plan": invitation.payment.subscription_plan.name,
                "billing_cycle": invitation.payment.billing_cycle,
            },
            status=status.HTTP_200_OK,
        )


class RegisterFromPaymentView(APIView):
    """
    POST /register/

    Completes business registration from a valid payment invitation.
    Returns JWT tokens on success.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken

        serializer = RegisterBusinessFromPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        audit_logger.info(
            "business_registered_from_payment user_id=%s email=%s ip=%s",
            user.pk,
            user.email,
            request.META.get("REMOTE_ADDR", ""),
        )

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class SubscriptionListView(APIView):
    """
    GET /subscriptions/

    List all subscriptions for the authenticated user's business.
    Super Admins see all subscriptions.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.subscriptions.models import Subscription

        if request.user.is_superuser:
            qs = Subscription.objects.select_related("business", "plan", "payment")
        else:
            qs = Subscription.objects.filter(
                business=request.user.business
            ).select_related("business", "plan", "payment")

        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        subscriptions = []
        for sub in qs:
            subscriptions.append({
                "id": sub.id,
                "business": sub.business.name,
                "plan": sub.plan.name,
                "billing_cycle": sub.billing_cycle,
                "amount": str(sub.amount),
                "start_date": sub.start_date,
                "end_date": sub.end_date,
                "status": sub.status,
                "is_active": sub.is_active,
                "auto_renew": sub.auto_renew,
                "created_at": sub.created_at,
            })

        return Response(subscriptions, status=status.HTTP_200_OK)


class CurrentSubscriptionView(APIView):
    """
    GET /subscriptions/current/

    Returns the current active subscription for the authenticated user's business.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.subscriptions.models import Subscription

        if request.user.is_superuser:
            return Response(
                {"detail": "Super Admins do not have a business subscription."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now().date()
        subscription = Subscription.objects.filter(
            business=request.user.business,
            status=SubscriptionStatus.ACTIVE,
            start_date__lte=now,
            end_date__gte=now,
        ).select_related("plan", "payment").first()

        if not subscription:
            return Response(
                {"detail": "No active subscription found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "id": subscription.id,
                "plan": subscription.plan.name,
                "billing_cycle": subscription.billing_cycle,
                "amount": str(subscription.amount),
                "start_date": subscription.start_date,
                "end_date": subscription.end_date,
                "status": subscription.status,
                "is_active": subscription.is_active,
                "auto_renew": subscription.auto_renew,
                "max_users": subscription.plan.max_users,
                "max_branches": subscription.plan.max_branches,
                "max_products": subscription.plan.max_products,
            },
            status=status.HTTP_200_OK,
        )
