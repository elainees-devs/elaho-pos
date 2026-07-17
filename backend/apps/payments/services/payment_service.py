import logging

from django.db import transaction
from django.utils import timezone

from apps.payments.models import (
    AuditAction,
    Payment,
    PaymentAuditLog,
    PaymentStatus,
    RegistrationInvitation,
)

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Handles payment lifecycle operations: verification, cancellation,
    refund, and invitation management.

    All state-changing operations are wrapped in database transactions
    to maintain consistency between payment status, audit logs, and
    invitation records.
    """

    @staticmethod
    @transaction.atomic
    def verify_payment(payment: Payment, verified_by) -> Payment:
        """
        Verify a pending payment and generate a registration invitation.

        Steps:
        1. Update payment status to Paid.
        2. Record verification timestamp and verifier.
        3. Create a registration invitation.
        4. Log the verification and invitation creation.
        5. Send the invitation email.

        Raises:
            ValueError: If the payment is not in Pending status.
        """
        payment = Payment.objects.select_for_update().get(pk=payment.pk)

        if payment.status != PaymentStatus.PENDING:
            raise ValueError(
                f"Cannot verify payment with status '{payment.get_status_display()}'. "
                f"Only pending payments can be verified."
            )

        payment.status = PaymentStatus.PAID
        payment.verified_at = timezone.now()
        payment.verified_by = verified_by
        payment.save(update_fields=[
            "status", "verified_at", "verified_by", "updated_at",
        ])

        PaymentAuditLog.objects.create(
            payment=payment,
            action=AuditAction.VERIFIED,
            performed_by=verified_by,
            description=f"Payment verified. Amount: {payment.currency} {payment.amount}.",
        )

        invitation, raw_token = RegistrationInvitation.create_for_payment(
            payment=payment,
            created_by=verified_by,
        )

        PaymentAuditLog.objects.create(
            payment=payment,
            action=AuditAction.INVITATION_SENT,
            performed_by=verified_by,
            description=f"Registration invitation sent to {payment.owner_email}.",
        )

        PaymentService._send_invitation_email(invitation, raw_token)

        logger.info(
            "Payment %s verified by %s. Invitation created.",
            payment.uuid,
            verified_by.email,
        )

        return payment

    @staticmethod
    @transaction.atomic
    def cancel_payment(payment: Payment, cancelled_by, reason: str = "") -> Payment:
        """
        Cancel a payment.

        Raises:
            ValueError: If the payment cannot be cancelled.
        """
        payment = Payment.objects.select_for_update().get(pk=payment.pk)

        if not payment.is_cancellable:
            raise ValueError(
                f"Cannot cancel payment with status '{payment.get_status_display()}'."
            )

        payment.status = PaymentStatus.CANCELLED
        payment.notes = f"{payment.notes}\n\nCancellation reason: {reason}".strip()
        payment.save(update_fields=["status", "notes", "updated_at"])

        PaymentAuditLog.objects.create(
            payment=payment,
            action=AuditAction.CANCELLED,
            performed_by=cancelled_by,
            description=f"Payment cancelled. {reason}".strip(),
        )

        logger.info(
            "Payment %s cancelled by %s.",
            payment.uuid,
            cancelled_by.email,
        )

        return payment

    @staticmethod
    @transaction.atomic
    def refund_payment(payment: Payment, refunded_by, reason: str = "") -> Payment:
        """
        Refund a paid payment.

        Raises:
            ValueError: If the payment cannot be refunded.
        """
        payment = Payment.objects.select_for_update().get(pk=payment.pk)

        if not payment.is_refundable:
            raise ValueError(
                f"Cannot refund payment with status '{payment.get_status_display()}'."
            )

        payment.status = PaymentStatus.REFUNDED
        payment.notes = f"{payment.notes}\n\nRefund reason: {reason}".strip()
        payment.save(update_fields=["status", "notes", "updated_at"])

        PaymentAuditLog.objects.create(
            payment=payment,
            action=AuditAction.REFUNDED,
            performed_by=refunded_by,
            description=f"Payment refunded. {reason}".strip(),
        )

        logger.info(
            "Payment %s refunded by %s.",
            payment.uuid,
            refunded_by.email,
        )

        return payment

    @staticmethod
    @transaction.atomic
    def resend_invitation(payment: Payment, resent_by) -> RegistrationInvitation:
        """
        Resend the registration invitation for a verified payment.

        Invalidates the previous unused invitation and creates a new one.

        Raises:
            ValueError: If the payment is not Paid or has no invitation.
        """
        payment = Payment.objects.select_for_update().get(pk=payment.pk)

        if payment.status != PaymentStatus.PAID:
            raise ValueError(
                f"Cannot resend invitation for payment with status "
                f"'{payment.get_status_display()}'. Only paid payments have invitations."
            )

        # Invalidate existing unused invitations.
        RegistrationInvitation.objects.filter(
            payment=payment,
            is_used=False,
        ).update(is_used=True)

        invitation, raw_token = RegistrationInvitation.create_for_payment(
            payment=payment,
            created_by=resent_by,
        )

        PaymentAuditLog.objects.create(
            payment=payment,
            action=AuditAction.INVITATION_RESENT,
            performed_by=resent_by,
            description=f"Registration invitation resent to {payment.owner_email}.",
        )

        PaymentService._send_invitation_email(invitation, raw_token)

        logger.info(
            "Invitation resent for payment %s by %s.",
            payment.uuid,
            resent_by.email,
        )

        return invitation

    @staticmethod
    def _send_invitation_email(invitation: RegistrationInvitation, raw_token: str) -> None:
        """
        Send the registration invitation email to the business owner.
        Silently logs errors without raising exceptions.
        """
        from django.core.mail import send_mail
        from django.template.loader import render_to_string

        try:
            context = {
                "owner_name": invitation.owner_name,
                "business_name": invitation.business_name,
                "token": raw_token,
                "protocol": "https",
                "domain": "app.elahopos.com",
            }

            subject = render_to_string(
                "payments/registration_invitation_subject.txt", context
            ).strip()
            html_body = render_to_string(
                "payments/registration_invitation_body.html", context
            )
            text_body = render_to_string(
                "payments/registration_invitation_body.txt", context
            )

            send_mail(
                subject=subject,
                message=text_body,
                html_message=html_body,
                from_email=None,
                recipient_list=[invitation.email],
            )
        except Exception:
            logger.exception(
                "Failed to send registration invitation email to %s",
                invitation.email,
            )
