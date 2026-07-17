from django.urls import path

from .views import (
    LoginView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterBusinessView,
    RegisterFromInviteView,
    SendVerificationView,
    ValidateInviteView,
    VerifyEmailView,
)

app_name = "authentication"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "send-verification/",
        SendVerificationView.as_view(),
        name="send_verification",
    ),
    path(
        "verify-email/",
        VerifyEmailView.as_view(),
        name="verify_email",
    ),
    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-change/",
        PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "invite/validate/",
        ValidateInviteView.as_view(),
        name="invite_validate",
    ),
    path(
        "register/",
        RegisterFromInviteView.as_view(),
        name="register_from_invite",
    ),
    path(
        "register-business/",
        RegisterBusinessView.as_view(),
        name="register_business",
    ),
]
