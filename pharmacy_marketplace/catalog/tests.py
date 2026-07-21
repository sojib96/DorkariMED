"""Initial placeholder tests for the catalog app."""

import unittest

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

# Phase 2 will add comprehensive tests for MasterMedicine, PharmacyMedicineListing


class CatalogAppSmokeTest(TestCase):
    """Smoke test to verify the catalog app loads properly."""

    def test_app_module_imports(self):
        """Verify the catalog app models module imports without errors."""
        try:
            from catalog.models import MasterMedicine, PharmacyMedicineListing  # noqa: F401
        except RuntimeError:
            raise unittest.SkipTest("catalog app excluded from INSTALLED_APPS")
        except ImproperlyConfigured:
            raise unittest.SkipTest("GDAL/PostGIS not available — skip GIS-dependent test")
        self.assertTrue(True)
