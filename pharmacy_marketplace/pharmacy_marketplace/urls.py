"""
Root URL configuration for pharmacy_marketplace.

Top-level URL dispatch for both API (versioned) and web (template-based) traffic.
Each app contributes its own URL patterns via its urlpatterns module, and
the web interface is organized into three tenant surfaces (customer, owner, admin).

GIS-dependent apps (pharmacies, catalog, search, notifications) are conditionally
included so that the project can run without GDAL for local testing. The CI
pipeline runs against a full PostGIS stack and includes all apps.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.health import health_check

# ── API v1 ──────────────────────────────────────────────────────────────────
api_v1_patterns = [
    path("auth/", include("accounts.urls.api", namespace="api-accounts")),
]

# Conditionally include GIS-dependent API routes
gps_api = [
    ("pharmacies", "pharmacies.urls.api", "api-pharmacies"),
    ("catalog", "catalog.urls.api", "api-catalog"),
    ("search", "search.urls.api", "api-search"),
    ("notifications", "notifications.urls.api", "api-notifications"),
]
for app_name, url_module, namespace in gps_api:
    if app_name in settings.INSTALLED_APPS:
        api_v1_patterns.append(path(f"{app_name}/", include(url_module, namespace=namespace)))

# ── Web surfaces ────────────────────────────────────────────────────────────
web_patterns = [
    # Authentication (web session-based)
    path("auth/", include("accounts.urls.auth", namespace="auth")),
]

# Conditionally include GIS-dependent web routes
gps_web = [
    ("pharmacies", "pharmacies.urls.webstore", "store"),
    ("pharmacies", "pharmacies.urls.owner", "owner"),
    ("catalog", "catalog.urls.owner", "owner-catalog"),
    ("search", "search.urls.webstore", "web-search"),
    ("catalog", "catalog.urls.admin", "admin-catalog"),
    ("notifications", "notifications.urls.admin", "admin-notifications"),
]
for app_name, url_module, namespace in gps_web:
    if app_name in settings.INSTALLED_APPS:
        web_patterns.append(path(f"{app_name}/", include(url_module, namespace=namespace)))

# Django admin — always included
web_patterns.insert(0, path("admin/", admin.site.urls))

# ── i18n ────────────────────────────────────────────────────────────────────
i18n_patterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

# ── Health check ────────────────────────────────────────────────────────────
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
