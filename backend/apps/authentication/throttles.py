from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class PasswordResetRequestThrottle(AnonRateThrottle):
    rate = "5/hour"
    scope = "password_reset_request"


class PasswordResetConfirmThrottle(AnonRateThrottle):
    rate = "10/hour"
    scope = "password_reset_confirm"


class PasswordChangeThrottle(UserRateThrottle):
    rate = "5/hour"
    scope = "password_change"


class EmailVerificationThrottle(AnonRateThrottle):
    rate = "10/hour"
    scope = "email_verification"


class ResendVerificationThrottle(UserRateThrottle):
    rate = "3/hour"
    scope = "resend_verification"
