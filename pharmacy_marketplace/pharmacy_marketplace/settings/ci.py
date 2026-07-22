"""
CI settings — like dev.py but with bumped throttle rates for rapid test execution.

Used by GitHub Actions CI (``pytest`` with PostGIS service container).
Inherits all modules from base.py including GIS-dependent apps (pharmacies, etc.)
and Django REST Framework defaults. Only throttle rates are overridden to prevent
test-suite exhaustion of per-IP rate limits during rapid sequential test execution.
"""

from .base import *  # noqa: F403, F401

# ── Bump throttle rates for rapid-fire test execution ──────────────────────
# Without this, test classes with 5+ sequential requests hit the 5/min
# per-IP throttle limit and fail with unexpected 429 responses.
# The values are still within reasonable bounds (100/min is 1.6 req/sec).
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login"] = "100/min"  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["registration"] = "100/min"  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["otp"] = "100/min"  # noqa: F405

# ── Developer-friendly settings ────────────────────────────────────────────
DEBUG = True
SECRET_KEY = "ci-test-key-not-for-production"
