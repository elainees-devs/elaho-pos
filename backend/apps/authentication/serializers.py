import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.roles.models import Role
from .models import TokenPurpose, UserInvitation, VerificationToken
from .services import (
    ADMIN_LOCKOUT_MSG,
    LoginLockoutService,
    POST_LOCKOUT_FAIL_MSG,
)

logger = logging.getLogger(__name__)

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

        # Account requires administrator unlock.
        if LoginLockoutService.requires_admin_unlock(user):
            raise serializers.ValidationError(
                {"detail": ADMIN_LOCKOUT_MSG}
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

        # Post-lockout expired — this is the final attempt before re-lock.
        if LoginLockoutService.is_lockout_expired(user):
            if not user.check_password(password):
                LoginLockoutService.record_failed_attempt(user)
                # Check if account now requires admin unlock.
                if LoginLockoutService.requires_admin_unlock(user):
                    raise serializers.ValidationError(
                        {"detail": ADMIN_LOCKOUT_MSG}
                    )
                raise serializers.ValidationError(
                    {"detail": POST_LOCKOUT_FAIL_MSG}
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

        request = self.context.get("request")
        protocol = request.scheme if request else "https"
        domain = request.get_host() if request else "localhost"

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

        try:
            send_mail(
                subject=subject,
                message=text_body,
                html_message=html_body,
                from_email=None,
                recipient_list=[user.email],
            )
        except Exception:
            logger.exception(
                "Failed to send password reset email to %s", user.email
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


class SendVerificationSerializer(serializers.Serializer):
    """
    Sends an email verification link to the authenticated user.

    User is identified from the JWT token (request.user).
    Always returns 200 to prevent enumeration.
    """

    def save(self, **kwargs):
        user = self.context["request"].user

        if user.email_verified:
            return

        request = self.context["request"]

        ip_address = None
        user_agent = ""
        if request:
            ip_address = request.META.get("REMOTE_ADDR")
            user_agent = request.META.get("HTTP_USER_AGENT", "")

        _, raw_token = VerificationToken.create_for_user(
            user=user,
            purpose=TokenPurpose.EMAIL_VERIFICATION,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        protocol = request.scheme if request else "https"
        domain = request.get_host() if request else "localhost"

        context = {
            "user": user,
            "token": raw_token,
            "protocol": protocol,
            "domain": domain,
        }

        subject = render_to_string(
            "email_verification/email_subject.txt", context
        ).strip()
        html_body = render_to_string(
            "email_verification/email_body.html", context
        )
        text_body = render_to_string(
            "email_verification/email_body.txt", context
        )

        try:
            send_mail(
                subject=subject,
                message=text_body,
                html_message=html_body,
                from_email=None,
                recipient_list=[user.email],
            )
        except Exception:
            logger.exception(
                "Failed to send verification email to %s", user.email
            )


class VerifyEmailSerializer(serializers.Serializer):
    """
    Verifies a user's email address using a token sent via email.

    Validates the token and marks the user's email as verified.
    """

    token = serializers.CharField()
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        token = attrs["token"]
        email = attrs["email"]

        user = User.objects.filter(email=email, is_active=True).first()
        if user is None:
            raise serializers.ValidationError(
                {"detail": "Invalid verification link."}
            )

        if user.email_verified:
            attrs["user"] = user
            attrs["already_verified"] = True
            return attrs

        token_instance = VerificationToken.validate_token(
            user=user,
            raw_token=token,
            purpose=TokenPurpose.EMAIL_VERIFICATION,
        )

        if token_instance is None:
            raise serializers.ValidationError(
                {"detail": "Invalid or expired verification link."}
            )

        attrs["user"] = user
        attrs["token_instance"] = token_instance
        attrs["already_verified"] = False
        return attrs

    def save(self, **kwargs):
        if self.validated_data.get("already_verified"):
            return

        user = self.validated_data["user"]
        token_instance = self.validated_data["token_instance"]

        user.email_verified = True
        user.save(update_fields=["email_verified"])

        token_instance.mark_used()

        self._send_welcome_email(user)

    def _send_welcome_email(self, user):
        request = self.context.get("request")
        protocol = request.scheme if request else "https"
        domain = request.get_host() if request else "localhost"
        context = {"user": user, "protocol": protocol, "domain": domain}

        try:
            subject = render_to_string(
                "welcome/email_subject.txt", context
            ).strip()
            html_body = render_to_string(
                "welcome/email_body.html", context
            )
            text_body = render_to_string(
                "welcome/email_body.txt", context
            )
            send_mail(
                subject=subject,
                message=text_body,
                html_message=html_body,
                from_email=None,
                recipient_list=[user.email],
            )
        except Exception:
            logger.exception(
                "Failed to send welcome email to %s", user.email
            )


class InviteUserSerializer(serializers.Serializer):
    """
    Sends an invitation email to a new user on behalf of the business owner.

    Creates a UserInvitation record (hashed token) and dispatches the email.
    The invited user has 48 hours to complete registration.
    """

    email = serializers.EmailField()
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.filter(is_active=True)
    )

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        email = attrs["email"]
        request = self.context["request"]
        business = getattr(request.user, "business", None)

        if business is None:
            raise serializers.ValidationError(
                {"detail": "Your account is not associated with a business."}
            )

        if get_user_model().objects.filter(
            email=email, business=business
        ).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists in your business."}
            )

        attrs["business"] = business
        return attrs

    def save(self, **kwargs):
        request = self.context["request"]
        email = self.validated_data["email"]
        role = self.validated_data["role"]
        business = self.validated_data["business"]
        ip_address = request.META.get("REMOTE_ADDR")

        _, raw_token = UserInvitation.create_invitation(
            email=email,
            role=role,
            business=business,
            invited_by=request.user,
            ip_address=ip_address,
        )

        protocol = request.scheme
        domain = request.get_host()

        context = {
            "invited_by": request.user,
            "business": business,
            "token": raw_token,
            "protocol": protocol,
            "domain": domain,
        }

        subject = render_to_string(
            "invitation/email_subject.txt", context
        ).strip()
        html_body = render_to_string("invitation/email_body.html", context)
        text_body = render_to_string("invitation/email_body.txt", context)

        try:
            send_mail(
                subject=subject,
                message=text_body,
                html_message=html_body,
                from_email=None,
                recipient_list=[email],
            )
        except Exception:
            logger.exception("Failed to send invitation email to %s", email)


class ValidateInviteSerializer(serializers.Serializer):
    """
    Validates an invitation token and returns the prefill data
    (email, role name, business name) for the registration form.
    """

    token = serializers.CharField()

    def validate(self, attrs):
        invitation = UserInvitation.validate_token(attrs["token"])

        if invitation is None:
            raise serializers.ValidationError(
                {"detail": "Invalid or expired invitation link."}
            )

        attrs["invitation"] = invitation
        return attrs


class RegisterFromInviteSerializer(serializers.Serializer):
    """
    Creates a new user account from a valid invitation token.

    On success the invitation is marked as used and the new user's
    email is pre-verified (they proved ownership by clicking the link).
    """

    token = serializers.CharField()
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        invitation = UserInvitation.validate_token(attrs["token"])

        if invitation is None:
            raise serializers.ValidationError(
                {"detail": "Invalid or expired invitation link."}
            )

        if get_user_model().objects.filter(email=invitation.email).exists():
            raise serializers.ValidationError(
                {"detail": "An account with this email already exists."}
            )

        attrs["invitation"] = invitation
        return attrs

    def save(self, **kwargs):
        invitation = self.validated_data["invitation"]

        with transaction.atomic():
            user = get_user_model().objects.create_user(
                email=invitation.email,
                password=self.validated_data["password"],
                first_name=self.validated_data["first_name"],
                last_name=self.validated_data["last_name"],
                phone=self.validated_data.get("phone", ""),
                business=invitation.business,
                role=invitation.role,
                email_verified=True,
            )
            invitation.mark_used()

        return user


class RegisterBusinessSerializer(serializers.Serializer):
    """
    Admin-assisted business registration.

    Creates a new Business and its owner User in a single transaction.
    This flow must be initiated by a superadmin.
    """

    # Business fields
    business_name = serializers.CharField(max_length=100)
    business_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    business_email = serializers.EmailField(required=False, allow_blank=True)
    business_address = serializers.CharField(required=False, allow_blank=True)
    kra_pin = serializers.CharField(max_length=20)

    # Owner fields
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate_business_name(self, value):
        return value.strip()

    def validate_email(self, value):
        return value.strip().lower()

    def validate_business_email(self, value):
        if value:
            return value.strip().lower()
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_kra_pin(self, value):
        return value.strip()

    def validate(self, attrs):
        email = attrs["email"]

        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "An account with this email already exists."}
            )

        from apps.businesses.models import Business

        if Business.objects.filter(name__iexact=attrs["business_name"]).exists():
            raise serializers.ValidationError(
                {"business_name": "A business with this name already exists."}
            )

        return attrs

    def save(self, **kwargs):
        from apps.businesses.models import Business
        from apps.roles.models import Role

        with transaction.atomic():
            business = Business.objects.create(
                name=self.validated_data["business_name"],
                phone=self.validated_data.get("business_phone", ""),
                email=self.validated_data.get("business_email", ""),
                address=self.validated_data.get("business_address", ""),
                kra_pin=self.validated_data["kra_pin"],
            )

            owner_role, _ = Role.objects.get_or_create(
                name="Owner",
                defaults={
                    "description": "Business owner with full access",
                    "level": 100,
                },
            )

            user = get_user_model().objects.create_user(
                email=self.validated_data["email"],
                password=self.validated_data["password"],
                first_name=self.validated_data["first_name"],
                last_name=self.validated_data["last_name"],
                phone=self.validated_data.get("phone", ""),
                business=business,
                role=owner_role,
                email_verified=True,
            )

            business.owner = user
            business.save(update_fields=["owner"])

        return user
