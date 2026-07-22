"""
Test settings — uses SQLite instead of PostGIS for non-GIS unit tests.

This settings module is NOT used by the CI pipeline (which runs against
a real PostGIS service). It exists only for local verification in
environments where GDAL/PostGIS are not available.

GIS-dependent apps (pharmacies, search) are excluded because their
models use PostGIS-specific fields (PointField) that require GDAL.
"""

from .base import *  # noqa: F403, F401

# Override database to SQLite for environments without GDAL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Remove GIS-dependent and transitively-dependent apps to avoid GDAL requirement
# Chain: pharmacies → catalog (FK) → notifications (FK)
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in (  # noqa: F405
    "django.contrib.gis",
    "pharmacies",          # uses gis_models.PointField — needs GDAL
    "catalog",             # FK to pharmacies.Pharmacy
    "notifications",       # FK to catalog.MasterMedicine
    "debug_toolbar",       # may not be installed
    "django_extensions",
)]

# Remove MIDDLEWARE that depends on gis or debug_toolbar
MIDDLEWARE = [m for m in MIDDLEWARE if "debug_toolbar" not in m]  # noqa: F405

# Bump throttle rates so tests don't hit rate limits during rapid-fire execution.
# Tests that specifically test throttle behaviour use their own overrides.
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login"] = "100/min"  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["registration"] = "100/min"  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["otp"] = "100/min"  # noqa: F405

DEBUG = True

SECRET_KEY = "test-key-not-for-production"
