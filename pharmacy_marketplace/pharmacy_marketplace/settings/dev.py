"""Development settings."""

from .base import *  # noqa: F403, F401

DEBUG = True

INSTALLED_APPS += ["debug_toolbar", "django_extensions"]  # noqa: F405

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

INTERNAL_IPS = env.list("INTERNAL_IPS", default=["127.0.0.1", "localhost"])  # noqa: F405

# Mail — print to console in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# More verbose logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
