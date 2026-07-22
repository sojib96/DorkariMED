"""
Pharmacies API v1 URL patterns — pharmacy CRUD and storefront.

Endpoints are under the ``/api/v1/pharmacies/`` path prefix.
Follows architect.md Section 5.3.
"""

from django.urls import path

from pharmacies.views import (
    PharmacyCreateView,
    PharmacyDeactivateView,
    PharmacyLocationUpdateView,
    PharmacyRetrieveUpdateView,
)

app_name = "api-pharmacies"

urlpatterns = [
    # ── CRUD ────────────────────────────────────────────────────────────────
    path("", PharmacyCreateView.as_view(), name="pharmacy-create"),
    # Combined detail (GET) + update (PATCH) at the same URL.
    # Single RetrieveUpdateAPIView handles both methods.
    path("<int:pk>/", PharmacyRetrieveUpdateView.as_view(), name="pharmacy-detail-update"),
    # ── Location ────────────────────────────────────────────────────────────
    path(
        "<int:pk>/location/",
        PharmacyLocationUpdateView.as_view(),
        name="pharmacy-location-update",
    ),
    # ── Deactivate ──────────────────────────────────────────────────────────
    path("<int:pk>/deactivate/", PharmacyDeactivateView.as_view(), name="pharmacy-deactivate"),
]
