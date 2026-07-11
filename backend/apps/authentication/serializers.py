from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers

User = get_user_model()

token_generator = PasswordResetTokenGenerator()


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
