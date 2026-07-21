"""Staging settings. Extends production with DEBUG=True for troubleshooting."""

from .production import *  # noqa: F403, F401

DEBUG = True

INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
