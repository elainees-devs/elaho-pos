from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CurrentSubscriptionView,
    PaymentDashboardView,
    PaymentViewSet,
    RegisterFromPaymentView,
    SubscriptionListView,
    SubscriptionPlanListView,
    ValidateRegistrationTokenView,
)

router = DefaultRouter()
router.register(r"", PaymentViewSet, basename="payments")

urlpatterns = router.urls + [
    # Dashboard
    path(
        "dashboard/",
        PaymentDashboardView.as_view(),
        name="payment_dashboard",
    ),
    # Subscription Plans
    path(
        "subscription-plans/",
        SubscriptionPlanListView.as_view(),
        name="subscription_plans",
    ),
    # Registration
    path(
        "registration-invitations/<str:token>/",
        ValidateRegistrationTokenView.as_view(),
        name="validate_registration_token",
    ),
    path(
        "register/",
        RegisterFromPaymentView.as_view(),
        name="register_from_payment",
    ),
    # Subscriptions
    path(
        "subscriptions/",
        SubscriptionListView.as_view(),
        name="subscription_list",
    ),
    path(
        "subscriptions/current/",
        CurrentSubscriptionView.as_view(),
        name="current_subscription",
    ),
]
