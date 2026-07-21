"""Initial placeholder tests for the notifications app."""

import unittest

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

# Phase 3 will add comprehensive tests for NotifySubscription and endpoints


class NotificationsAppSmokeTest(TestCase):
    """Smoke test to verify the notifications app loads properly."""

    def test_app_module_imports(self):
        """Verify the notifications app models module imports without errors."""
        try:
            from notifications.models import NotifySubscription  # noqa: F401
        except RuntimeError:
            raise unittest.SkipTest("notifications app excluded from INSTALLED_APPS")
        except ImproperlyConfigured:
            raise unittest.SkipTest("GDAL/PostGIS not available — skip GIS-dependent test")
        self.assertTrue(True)
