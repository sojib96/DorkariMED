"""Pharmacy owner dashboard URL patterns.

URLs under this module serve the pharmacy owner dashboard.
They are included at root level (/) with namespace "owner".
Dashboard views are defined in accounts/views/web.py for now.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import path
from django.views.generic import TemplateView

from accounts.views.web import OwnerDashboardView


class ProfilePlaceholderView(LoginRequiredMixin, TemplateView):
    """Placeholder profile page — Phase 2 will add full editing."""
    template_name = "owner/profile.html"
    login_url = "/owner/login/"

app_name = "owner"

urlpatterns = [
    # Owner dashboard — auth-protected, shows pharmacy management shell
    path("owner/dashboard/", OwnerDashboardView.as_view(), name="dashboard"),
    # Profile placeholder — Phase 2 will enhance
    path("owner/profile/", ProfilePlaceholderView.as_view(), name="profile"),
]

# Phase 2 will add: medicines listing, bulk upload, etc.
