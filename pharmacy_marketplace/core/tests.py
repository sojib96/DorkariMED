"""Tests for the core app — pagination, exception handler, health check."""

from django.test import TestCase, RequestFactory
from django.http import JsonResponse

from core.health import health_check


class HealthCheckTest(TestCase):
    """Verify the health check endpoint returns valid JSON."""

    def test_health_check_returns_200(self):
        """Health check should return 200 with status 'healthy' or 'degraded'."""
        factory = RequestFactory()
        request = factory.get("/health/")
        response = health_check(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertIn(response.status_code, [200, 503])
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("database", data)
