from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.payments.models import RegistrationInvitation
from apps.payments.services.registration_service import RegistrationService

User = get_user_model()


class ValidateRegistrationTokenSerializer(serializers.Serializer):
    """
    Validates a registration invitation token and returns prefill data.
    """

    token = serializers.CharField()

    def validate(self, attrs):
        invitation = RegistrationInvitation.validate_token(attrs["token"])

        if invitation is None:
            raise serializers.ValidationError(
                {"detail": "Invalid or expired registration link."}
            )

        attrs["invitation"] = invitation
        return attrs


class RegisterBusinessFromPaymentSerializer(serializers.Serializer):
    """
    Creates a new business, owner, and subscription from a valid
    payment invitation token.
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
        invitation = RegistrationInvitation.validate_token(attrs["token"])

        if invitation is None:
            raise serializers.ValidationError(
                {"detail": "Invalid or expired registration link."}
            )

        if User.objects.filter(email=invitation.email).exists():
            raise serializers.ValidationError(
                {"detail": "An account with this email already exists."}
            )

        attrs["invitation"] = invitation
        return attrs

    def save(self, **kwargs):
        invitation = self.validated_data["invitation"]

        business, user = RegistrationService.register_from_invitation(
            invitation=invitation,
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            phone=self.validated_data.get("phone", ""),
            password=self.validated_data["password"],
        )

        return user
