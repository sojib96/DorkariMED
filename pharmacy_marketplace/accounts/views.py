"""
Accounts app views — registration, login, profile, and OTP verification.

Uses DRF generic views and JWT token issuance via ``djangorestframework-simplejwt``.
"""

import logging
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import OTPCode, User
from accounts.serializers import (
    CustomerRegistrationSerializer,
    LoginSerializer,
    PharmacyOwnerRegistrationSerializer,
    SendOtpSerializer,
    UserProfileSerializer,
    VerifyOtpSerializer,
)
from accounts.sms.utils import get_sms_sender
from accounts.throttles import LoginRateThrottle, OtpRateThrottle, RegistrationRateThrottle

logger = logging.getLogger(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────


def _get_tokens_for_user(user):
    """Issue JWT access + refresh tokens for the given user."""
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


# ── Registration ────────────────────────────────────────────────────────────────


class CustomerRegistrationView(generics.CreateAPIView):
    """Register a new customer account.

    POST /api/v1/auth/register/customer/
    Accepts: {phone, full_name, password}
    Returns: user data (without password) — no JWT issued here;
             the frontend redirects to OTP verification next.
    """

    queryset = User.objects.all()
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegistrationRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "phone": user.phone,
                "full_name": user.full_name,
                "role": user.role,
                "is_phone_verified": user.is_phone_verified,
                "message": "Account created. Please verify your phone via OTP.",
            },
            status=status.HTTP_201_CREATED,
        )


class PharmacyOwnerRegistrationView(generics.CreateAPIView):
    """Register a new pharmacy owner account.

    POST /api/v1/auth/register/pharmacy-owner/
    Accepts: {phone, full_name, password, pharmacy: {...}}
    Returns: user data + pharmacy data (without password).
             Frontend redirects to OTP verification next.
    """

    queryset = User.objects.all()
    serializer_class = PharmacyOwnerRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegistrationRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create the pharmacy if nested data is provided
        pharmacy_data = request.data.get("pharmacy")
        if pharmacy_data:
            from pharmacies.serializers import PharmacyRegistrationSerializer

            pharm_serializer = PharmacyRegistrationSerializer(
                data=pharmacy_data,
                context={"request": request},
            )
            pharm_serializer.is_valid(raise_exception=True)
            pharm_serializer.save(owner=user)

        return Response(
            {
                "id": user.id,
                "phone": user.phone,
                "full_name": user.full_name,
                "role": user.role,
                "is_phone_verified": user.is_phone_verified,
                "message": "Account created. Please verify your phone via OTP.",
            },
            status=status.HTTP_201_CREATED,
        )


# ── Login ───────────────────────────────────────────────────────────────────────


class LoginView(generics.GenericAPIView):
    """Authenticate and return JWT tokens.

    POST /api/v1/auth/login/
    Accepts: {phone, password}
    Returns: {access, refresh, user: {...}}
    """

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = _get_tokens_for_user(user)
        return Response(
            {
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user": UserProfileSerializer(user).data,
            }
        )


# ── Profile ─────────────────────────────────────────────────────────────────────


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile.

    GET/PATCH /api/v1/auth/profile/
    """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ── OTP Endpoints ───────────────────────────────────────────────────────────────


class SendOtpView(APIView):
    """Generate and send a 6-digit OTP code via SMS.

    POST /api/v1/auth/otp/send/
    Accepts: {phone}
    Behavior:
        - Invalidates any prior unverified OTP codes for this phone
        - Generates a 6-digit numeric code
        - Stores a hashed copy
        - Sends plaintext via SmsSender (ConsoleSmsSender in dev)
    Rate limit: 5 OTP requests per phone per hour (view-level check)
               + 5 requests per minute per IP (throttle class)
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = [OtpRateThrottle]

    def post(self, request):
        serializer = SendOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]

        # ── Phone-level rate limiting (cache-based) ────────────────────────
        # Allow max 5 OTP requests per hour per phone number.
        from django.core.cache import cache

        cache_key = f"otp_rate_phone_{phone}"
        phone_attempts = cache.get(cache_key, 0)
        if phone_attempts >= 5:
            return Response(
                {"error": {"code": "rate_limited",
                           "message": "Too many OTP requests for this phone. Try again later.",
                           "details": None}},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        cache.set(cache_key, phone_attempts + 1, timeout=3600)  # 1 hour window

        # ── Invalidate prior unverified codes ──────────────────────────────
        OTPCode.objects.filter(phone=phone, is_verified=False).update(is_verified=True)

        # ── Generate and store code ────────────────────────────────────────
        plain_code = get_random_string(length=6, allowed_chars="0123456789")
        hashed_code = make_password(plain_code)
        expires_at = timezone.now() + timedelta(minutes=10)

        OTPCode.objects.create(
            phone=phone,
            code=hashed_code,
            expires_at=expires_at,
        )

        # ── Send via SMS sender ────────────────────────────────────────────
        sms_sender = get_sms_sender()
        message = f"Your Pharmacy Marketplace verification code is: {plain_code}"
        sms_sender.send_sms(phone, message)

        logger.info("OTP sent to %s (dev code: %s)", phone, plain_code)

        return Response(
            {
                "message": "Verification code sent.",
                "phone": phone,
                "expires_in_minutes": 10,
            },
            status=status.HTTP_200_OK,
        )


class VerifyOtpView(APIView):
    """Verify a 6-digit OTP code.

    POST /api/v1/auth/otp/verify/
    Accepts: {phone, code}
    Behavior:
        - Looks up the most recent unverified, non-expired OTPCode
        - Verifies the plaintext code against the stored hash
        - On success: marks OTPCode as verified + sets phone_verified on User
        - On failure: increments attempts, locks out after 5 failures
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = [OtpRateThrottle]

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]

        # ── Find the most recent active OTP code ───────────────────────────
        otp_code = (
            OTPCode.objects.filter(
                phone=phone,
                is_verified=False,
                expires_at__gt=timezone.now(),
            )
            .order_by("-created_at")
            .first()
        )

        if otp_code is None:
            # No valid OTP code found — might be expired or already used
            return Response(
                {"error": {"code": "otp_not_found",
                           "message": "No valid verification code found. Request a new one.",
                           "details": None}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Check lockout ──────────────────────────────────────────────────
        if otp_code.attempts >= 5:
            return Response(
                {"error": {"code": "otp_locked",
                           "message": "Too many incorrect attempts. Request a new code.",
                           "details": None}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Verify the code ────────────────────────────────────────────────
        if not check_password(code, otp_code.code):
            otp_code.attempts += 1
            otp_code.save(update_fields=["attempts"])
            remaining = 5 - otp_code.attempts
            return Response(
                {"error": {"code": "invalid_otp",
                           "message": f"Invalid code. {remaining} attempt(s) remaining.",
                           "details": None}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Success ────────────────────────────────────────────────────────
        otp_code.is_verified = True
        otp_code.save(update_fields=["is_verified"])

        # Mark the user as phone-verified if they exist
        User.objects.filter(phone=phone).update(is_phone_verified=True)

        return Response(
            {
                "message": "Phone verified successfully.",
                "phone": phone,
                "is_phone_verified": True,
            },
            status=status.HTTP_200_OK,
        )
