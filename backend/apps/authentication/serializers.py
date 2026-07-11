from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .services import LoginLockoutService, PERMANENT_LOCKOUT_MSG

User = get_user_model()

token_generator = PasswordResetTokenGenerator()

LOGIN_ERROR_MSG = "Invalid email or password."


class LoginSerializer(serializers.Serializer):
    """
    Authenticates a user with email + password, enforcing lockout policy.

    Raises ValidationError on any auth failure with appropriate message.
    Returns validated user on success.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        user = LoginLockoutService._get_user_for_login(email)

        # Always run password hash to prevent timing attacks.
        if user is None:
            User().set_password(password)
            raise serializers.ValidationError(
                {"detail": LOGIN_ERROR_MSG}
            )

        # Permanently locked by the lockout system — reject all attempts.
        if LoginLockoutService.is_permanently_locked(user):
            raise serializers.ValidationError(
                {"detail": PERMANENT_LOCKOUT_MSG}
            )

        # Temporarily locked (still within lockout window).
        if LoginLockoutService.is_locked_out(user):
            remaining = LoginLockoutService.get_lockout_remaining_seconds(user)
            minutes, seconds = divmod(remaining, 60)
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Account is temporarily locked due to too many "
                        f"failed login attempts. Try again in {minutes}m {seconds}s."
                    )
                }
            )

        # Post-lockout expired — this is the final attempt.
        if LoginLockoutService.is_lockout_expired(user):
            if not user.check_password(password):
                LoginLockoutService.record_failed_attempt(user)
                raise serializers.ValidationError(
                    {"detail": PERMANENT_LOCKOUT_MSG}
                )
            # Correct password on post-lockout attempt → reset everything.
            LoginLockoutService.reset_failed_attempts(user)
            attrs["user"] = user
            return attrs

        # Inactive user (admin-deactivated, not lockout-deactivated).
        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": LOGIN_ERROR_MSG}
            )

        # Verify password.
        if not user.check_password(password):
            user = LoginLockoutService.record_failed_attempt(user)

            # Re-check lockout after the attempt (may have just locked).
            if LoginLockoutService.is_locked_out(user):
                remaining = LoginLockoutService.get_lockout_remaining_seconds(user)
                minutes, seconds = divmod(remaining, 60)
                raise serializers.ValidationError(
                    {
                        "detail": (
                            "Account is temporarily locked due to too many "
                            f"failed login attempts. Try again in {minutes}m {seconds}s."
                        )
                    }
                )

            raise serializers.ValidationError(
                {"detail": LOGIN_ERROR_MSG}
            )

        # Success — reset failed attempts.
        LoginLockoutService.reset_failed_attempts(user)

        attrs["user"] = user
        return attrs

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()

    def save(self, **kwargs):
        email = self.validated_data["email"]
        user = User.objects.filter(email=email, is_active=True).first()

        if user is None:
            return

        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())

        protocol = self.context.get("protocol", "https")
        domain = self.context.get("domain", "elahopos.com")

        context = {
            "user": user,
            "token": token,
            "uid": uid,
            "protocol": protocol,
            "domain": domain,
        }

        subject = render_to_string(
            "password_reset/email_subject.txt", context
        ).strip()
        html_body = render_to_string("password_reset/email_body.html", context)
        text_body = render_to_string("password_reset/email_body.txt", context)

        send_mail(
            subject=subject,
            message=text_body,
            html_message=html_body,
            from_email=None,
            recipient_list=[user.email],
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.strip().lower()

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        token = attrs["token"]
        email = attrs["email"]

        user = User.objects.filter(email=email, is_active=True).first()
        if user is None:
            raise serializers.ValidationError(
                {"token": "Invalid or expired token."}
            )

        if not token_generator.check_token(user, token):
            raise serializers.ValidationError(
                {"token": "Invalid or expired token."}
            )

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        password = self.validated_data["password"]
        user.set_password(password)
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def validate_current_password(self, value):
        if not self.user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value, user=self.user)
        return value

    def save(self, **kwargs):
        password = self.validated_data["new_password"]
        self.user.set_password(password)
        self.user.save()
        return self.user
