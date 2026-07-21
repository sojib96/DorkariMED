"""Initial placeholder tests for the notifications app."""

from django.test import TestCase

# Phase 3 will add comprehensive tests for NotifySubscription and endpoints


class NotificationsAppSmokeTest(TestCase):
    """Smoke test to verify the notifications app loads properly."""

    def test_app_module_imports(self):
        """Verify the notifications app models module imports without errors."""
        from notifications.models import NotifySubscription  # noqa: F401
        self.assertTrue(True)
