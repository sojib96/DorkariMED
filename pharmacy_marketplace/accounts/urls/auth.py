"""
Web (session-based) authentication URL patterns.

These serve the Django-template-based login/registration forms for all
three web surfaces (customer, owner, admin). The API counterpart is in
``accounts/urls/api.py``.

URL structure:
  /customer/login/    → Customer login
  /customer/register/ → Customer registration
  /owner/login/       → Owner login
  /owner/register/    → Owner registration
  /logout/            → Shared logout
  /login/             → Django built-in login (fallback, admin uses this)
  /logout/            → Django built-in logout

Owner dashboard is in pharmacies/urls/owner.py (owner namespace).
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from accounts.views.web import (
    CustomerLoginView,
    CustomerRegistrationView,
    OwnerLoginView,
    OwnerRegistrationView,
    logout_view,
)

app_name = "auth"

urlpatterns = [
    # Customer auth
    path("customer/login/", CustomerLoginView.as_view(), name="customer-login"),
    path("customer/register/", CustomerRegistrationView.as_view(), name="customer-register"),
    # Owner auth
    path("owner/login/", OwnerLoginView.as_view(), name="owner-login"),
    path("owner/register/", OwnerRegistrationView.as_view(), name="owner-register"),
    # Logout — shared across all surfaces
    path("logout/", logout_view, name="logout"),
    # Django built-in auth views (fallback, used by admin)
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="django-logout"),
]
