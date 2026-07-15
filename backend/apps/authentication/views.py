from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    SendVerificationSerializer,
    VerifyEmailSerializer,
)
from .throttles import (
    EmailVerificationThrottle,
    PasswordChangeThrottle,
    PasswordResetConfirmThrottle,
    PasswordResetRequestThrottle,
    ResendVerificationThrottle,
)


class LoginView(APIView):
    """
    POST /api/v1/auth/login/

    Custom login endpoint with escalating lockout protection.

    Enforces:
    - Account lockout after configurable failed attempts
    - Escalating lockout cycles with admin notification
    - Generic error messages to prevent enumeration
    - Rate limiting via throttle
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRequestThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            # Auth failures are always 401/403; validation errors are 400.
            detail = serializer.errors.get("detail")
            if isinstance(detail, list):
                detail = detail[0]
            if isinstance(detail, str):
                if "contact" in detail.lower() and "administrator" in detail.lower():
                    return Response(
                        {"detail": detail},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                if (
                    "Invalid email or password" in detail
                    or "locked" in detail.lower()
                    or "Try again in" in detail
                ):
                    return Response(
                        {"detail": detail},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        tokens = serializer.get_tokens(user)

        return Response(tokens, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    POST /api/v1/auth/password-reset/

    Request a password reset link. Always returns 200 to prevent enumeration.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRequestThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "detail": (
                    "If an account with that email exists, "
                    "a password reset link has been sent."
                )
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    POST /api/v1/auth/password-reset/confirm/

    Confirm a password reset with a valid token and new password.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetConfirmThrottle]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


class PasswordChangeView(APIView):
    """
    POST /api/v1/auth/password-change/

    Change password for authenticated user. Requires current password.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [PasswordChangeThrottle]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            user=request.user,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class SendVerificationView(APIView):
    """
    POST /api/v1/auth/send-verification/

    Send an email verification link to the authenticated user.
    Always returns 200 to prevent enumeration.
    Skips if the email is already verified.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [ResendVerificationThrottle]

    def post(self, request):
        serializer = SendVerificationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "detail": "Verification email sent."
            },
            status=status.HTTP_200_OK,
        )


class VerifyEmailView(APIView):
    """
    POST /api/v1/auth/verify-email/

    Verify a user's email address using a token from the verification email.
    Always returns 200 if already verified. Returns 400 for invalid tokens.
    """

    permission_classes = [AllowAny]
    throttle_classes = [EmailVerificationThrottle]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        already_verified = serializer.validated_data.get("already_verified", False)

        if already_verified:
            return Response(
                {"detail": "Email is already verified."},
                status=status.HTTP_200_OK,
            )

        serializer.save()

        return Response(
            {"detail": "Email verified successfully."},
            status=status.HTTP_200_OK,
        )
