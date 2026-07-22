"""
Web (session-based) authentication URL patterns.

These serve the Django-template-based login/registration forms for all
three web surfaces (customer, owner, admin). The API counterpart is in
``accounts/urls/api.py``.
"""

from django.contrib.auth import views as auth_views
from django.urls import path

app_name = "auth"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
