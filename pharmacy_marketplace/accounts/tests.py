"""Initial placeholder tests for the accounts app."""

from django.test import TestCase

# Phase 1 will add comprehensive tests for User model, JWT, OTP flow


class AccountsAppSmokeTest(TestCase):
    """Smoke test to verify the accounts app loads properly."""

    def test_app_module_imports(self):
        """Verify the accounts app models module imports without errors."""
        from accounts.models import User  # noqa: F401
        self.assertTrue(True)
