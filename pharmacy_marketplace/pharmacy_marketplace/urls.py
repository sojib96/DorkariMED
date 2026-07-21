"""
Root URL configuration for pharmacy_marketplace.

Top-level URL dispatch for both API (versioned) and web (template-based) traffic.
Each app contributes its own URL patterns via its urlpatterns module, and
the web interface is organized into three tenant surfaces (customer, owner, admin).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# ── API v1 ──────────────────────────────────────────────────────────────────
api_v1_patterns = [
    path("accounts/", include("accounts.urls.api", namespace="api-accounts")),
    path("pharmacies/", include("pharmacies.urls.api", namespace="api-pharmacies")),
    path("catalog/", include("catalog.urls.api", namespace="api-catalog")),
    path("search/", include("search.urls.api", namespace="api-search")),
    path("notifications/", include("notifications.urls.api", namespace="api-notifications")),
]

# ── Web surfaces ────────────────────────────────────────────────────────────
web_patterns = [
    # Customer-facing site
    path("", include("pharmacies.urls.webstore", namespace="store")),
    path("search/", include("search.urls.webstore", namespace="web-search")),
    # Pharmacy owner dashboard
    path("owner/", include("pharmacies.urls.owner", namespace="owner")),
    path("owner/catalog/", include("catalog.urls.owner", namespace="owner-catalog")),
    # Admin dashboard (Django admin + custom admin views)
    path("admin/", admin.site.urls),
    path("admin/", include("catalog.urls.admin", namespace="admin-catalog")),
    path("admin/", include("notifications.urls.admin", namespace="admin-notifications")),
    # Authentication (web session-based)
    path("auth/", include("accounts.urls.auth", namespace="auth")),
]

# ── i18n ────────────────────────────────────────────────────────────────────
i18n_patterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

# ── Health check ────────────────────────────────────────────────────────────
from core.health import health_check

health_patterns = [
    path("health/", health_check, name="health-check"),
]

# ── Top-level ───────────────────────────────────────────────────────────────
urlpatterns = health_patterns + [
    path("api/v1/", include(api_v1_patterns)),
    path("", include(web_patterns)),
    path("", include(i18n_patterns)),
]

# ── Dev / debug toolbar ─────────────────────────────────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    try:
        import debug_toolbar
        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
