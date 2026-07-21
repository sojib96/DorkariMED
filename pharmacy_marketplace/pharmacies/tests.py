"""Initial placeholder tests for the pharmacies app."""

import unittest

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

# Phase 1 will add comprehensive tests for Pharmacy model, CRUD


class PharmaciesAppSmokeTest(TestCase):
    """Smoke test to verify the pharmacies app loads properly."""

    def test_app_module_imports(self):
        """Verify the pharmacies app models module imports without errors."""
        try:
            from pharmacies.models import Pharmacy  # noqa: F401
        except ImproperlyConfigured:
            raise unittest.SkipTest("GDAL/PostGIS not available — skip GIS-dependent test")
        self.assertTrue(True)
