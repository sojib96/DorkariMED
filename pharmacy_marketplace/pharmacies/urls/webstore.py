"""Customer-facing web storefront URL patterns.

URLs under this module serve the customer website (public browsing, search, etc.).
They are included at root level (/) with namespace "store".
"""

from django.urls import path
from django.views.generic import TemplateView

app_name = "store"

urlpatterns = [
    # Customer home page
    path("", TemplateView.as_view(template_name="customer/home.html"), name="home"),
]

# Phase 3 will add: pharmacy detail page, search results, medicine detail, etc.
