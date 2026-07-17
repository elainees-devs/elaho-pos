import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.businesses.models import Business
from apps.payments.models import (
    Payment,
    PaymentStatus,
    RegistrationInvitation,
)
from apps.roles.models import Role
from apps.subscriptions.models import Subscription, SubscriptionPlan

User = get_user_model()

logger = logging.getLogger(__name__)


class RegistrationService:
    """
    Handles business registration from a verified payment invitation.

    Creates the Business, Owner User, default Branch, Owner role assignment,
    and active Subscription in a single atomic transaction.
    """

    @staticmethod
    @transaction.atomic
    def register_from_invitation(
        invitation: RegistrationInvitation,
        first_name: str,
        last_name: str,
        phone: str,
        password: str,
    ) -> tuple:
        """
        Complete business registration from a valid invitation.

        Creates:
        1. Business
        2. Business Owner (User)
        3. Default Branch
        4. Owner Role assignment
        5. Active Subscription

        Returns:
            (business, user) tuple.
        """
        payment = invitation.payment
        plan = payment.subscription_plan

        # 1. Create Business
        business = Business.objects.create(
            name=invitation.business_name,
            email=invitation.email,
            phone=payment.owner_phone,
        )

        # 2. Get or create Owner role
        owner_role, _ = Role.objects.get_or_create(
            name="Owner",
            defaults={
                "description": "Business owner with full access",
                "level": 100,
            },
        )

        # 3. Create Owner User
        user = User.objects.create_user(
            email=invitation.email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            business=business,
            role=owner_role,
            email_verified=True,
        )

        # 4. Link business to owner
        business.owner = user
        business.save(update_fields=["owner"])

        # 5. Create default branch
        from apps.businesses.models import Branch
        Branch.objects.create(
            business=business,
            name="Main Branch",
            is_default=True,
        )

        # 6. Create Subscription
        if payment.billing_cycle == "annual":
            end_date = timezone.now().date() + timedelta(days=365)
        else:
            end_date = timezone.now().date() + timedelta(days=30)

        Subscription.objects.create(
            business=business,
            payment=payment,
            plan=plan,
            billing_cycle=payment.billing_cycle,
            amount=payment.amount,
            start_date=timezone.now().date(),
            end_date=end_date,
            status="active",
        )

        # 7. Mark invitation as used
        invitation.mark_used()

        logger.info(
            "Business '%s' registered by %s via invitation from payment %s.",
            business.name,
            user.email,
            payment.uuid,
        )

        return business, user
