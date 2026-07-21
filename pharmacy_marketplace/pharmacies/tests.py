"""Initial placeholder tests for the pharmacies app."""

from django.test import TestCase

# Phase 1 will add comprehensive tests for Pharmacy model, CRUD


class PharmaciesAppSmokeTest(TestCase):
    """Smoke test to verify the pharmacies app loads properly."""

    def test_app_module_imports(self):
        """Verify the pharmacies app models module imports without errors."""
        from pharmacies.models import Pharmacy  # noqa: F401
        self.assertTrue(True)
