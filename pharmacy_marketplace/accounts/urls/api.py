"""
Accounts API v1 URL patterns — authentication and OTP.

All endpoints are under the ``/api/v1/auth/`` path prefix (wired in the
root URLconf). This follows architect.md Section 5.2.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    CustomerRegistrationView,
    LoginView,
    PharmacyOwnerRegistrationView,
    SendOtpView,
    UserProfileView,
    VerifyOtpView,
)

app_name = "api-accounts"

urlpatterns = [
    # ── Registration ────────────────────────────────────────────────────────
    path("register/customer/", CustomerRegistrationView.as_view(), name="customer-register"),
    path(
        "register/pharmacy-owner/",
        PharmacyOwnerRegistrationView.as_view(),
        name="pharmacy-owner-register",
    ),
    # ── Login / Token ───────────────────────────────────────────────────────
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # ── Profile ─────────────────────────────────────────────────────────────
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    # ── OTP ─────────────────────────────────────────────────────────────────
    path("otp/send/", SendOtpView.as_view(), name="otp-send"),
    path("otp/verify/", VerifyOtpView.as_view(), name="otp-verify"),
]
