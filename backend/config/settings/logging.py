from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format": (
                "{levelname} {asctime} {module} "
                "{process:d} {thread:d} {message}"
            ),
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },

    "handlers": {
        # Console output
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },

        # General application logs
        "file": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "app.log",
            "formatter": "verbose",
        },

        # Error logs
        "errors": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "errors.log",
            "formatter": "verbose",
            "level": "ERROR",
        },

        # Audit logs
        "audit": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "audit.log",
            "formatter": "verbose",
        },

        # Sales logs
        "sales": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "sales.log",
            "formatter": "verbose",
        },

        # Inventory logs
        "inventory": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "inventory.log",
            "formatter": "verbose",
        },

        # M-Pesa synchronization logs
        "mpesa": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "mpesa.log",
            "formatter": "verbose",
        },

        # eTIMS logs
        "etims": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "etims.log",
            "formatter": "verbose",
        },
    },

    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },

        "django.request": {
            "handlers": ["errors"],
            "level": "ERROR",
            "propagate": False,
        },

        "audit": {
            "handlers": ["audit"],
            "level": "INFO",
            "propagate": False,
        },

        "sales": {
            "handlers": ["sales"],
            "level": "INFO",
            "propagate": False,
        },

        "inventory": {
            "handlers": ["inventory"],
            "level": "INFO",
            "propagate": False,
        },

        "mpesa": {
            "handlers": ["mpesa"],
            "level": "INFO",
            "propagate": False,
        },

        "etims": {
            "handlers": ["etims"],
            "level": "INFO",
            "propagate": False,
        },
    },

    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}