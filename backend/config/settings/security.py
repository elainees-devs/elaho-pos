"""
Security settings shared across environments.
Override in dev.py or prod.py if necessary.
"""

import os
from datetime import timedelta

# ------------------------------------------------------------------
# Authentication
# ------------------------------------------------------------------

AUTH_USER_MODEL = "users.User"

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/auth/login/"

# ------------------------------------------------------------------
# Password Validation
# ------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ------------------------------------------------------------------
# Session Security
# ------------------------------------------------------------------

SESSION_COOKIE_AGE = 60 * 60 * 12  # 12 hours

SESSION_SAVE_EVERY_REQUEST = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

SESSION_COOKIE_HTTPONLY = True

# ------------------------------------------------------------------
# CSRF
# ------------------------------------------------------------------

CSRF_COOKIE_HTTPONLY = True

CSRF_USE_SESSIONS = False

# ------------------------------------------------------------------
# Clickjacking Protection
# ------------------------------------------------------------------

X_FRAME_OPTIONS = "DENY"

# ------------------------------------------------------------------
# Browser Security Headers
# ------------------------------------------------------------------

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_BROWSER_XSS_FILTER = True

SECURE_REFERRER_POLICY = "same-origin"

# ------------------------------------------------------------------
# Audit Trail Settings
# ------------------------------------------------------------------

AUDIT_LOG_ENABLED = True

AUDIT_LOG_USER_IP = True

AUDIT_LOG_USER_AGENT = True

# ------------------------------------------------------------------
# JSON Web Tokens (JWT)
# ------------------------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# ------------------------------------------------------------------
# API Security
# ------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}