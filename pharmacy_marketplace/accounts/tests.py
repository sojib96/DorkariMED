"""
Comprehensive tests for the accounts app: User model, registration, login,
profile, OTP send/verify, rate limiting, and lockout behaviour.
"""

from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import OTPCode, User


class UserModelTests(TestCase):
    """B1-01: User model structure, manager, and constraints."""

    def setUp(self):
        self.client = APIClient()

    def test_create_customer_user(self):
        """A customer user can be created with phone as the identifier."""
        user = User.objects.create_user(
            phone="01712345678",
            password="testpass123",
            full_name="Test Customer",
            role=User.Role.CUSTOMER,
        )
        self.assertEqual(user.phone, "01712345678")
        self.assertEqual(user.role, "customer")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNone(user.email)
        self.assertIsNone(user.default_latitude)

    def test_create_pharmacy_owner_user(self):
        """A pharmacy owner user can be created."""
        user = User.objects.create_user(
            phone="01798765432",
            password="ownerpass456",
            full_name="Test Owner",
            role=User.Role.PHARMACY_OWNER,
        )
        self.assertEqual(user.role, "pharmacy_owner")

    def test_create_superuser(self):
        """A superuser with admin role can be created."""
        admin = User.objects.create_superuser(
            phone="01700000000",
            password="adminpass789",
            full_name="Platform Admin",
        )
        self.assertEqual(admin.role, "admin")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)

    def test_user_str(self):
        """String representation shows name and phone."""
        user = User.objects.create_user(
            phone="01711111111",
            password="testpass",
            full_name="John Doe",
            role=User.Role.CUSTOMER,
        )
        self.assertIn("John Doe", str(user))
        self.assertIn("01711111111", str(user))

    def test_phone_unique_constraint(self):
        """Duplicate phone numbers are rejected."""
        User.objects.create_user(
            phone="01712345678", password="pass1",
            full_name="User One", role=User.Role.CUSTOMER,
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                phone="01712345678", password="pass2",
                full_name="User Two", role=User.Role.CUSTOMER,
            )

    def test_email_is_optional(self):
        """Email field can be null."""
        user = User.objects.create_user(
            phone="01722222222",
            password="testpass",
            full_name="No Email",
            role=User.Role.CUSTOMER,
        )
        self.assertIsNone(user.email)


class CustomerRegistrationTests(TestCase):
    """B1-02, B1-03: Customer registration via API."""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/register/customer/"
        self.valid_payload = {
            "phone": "01712345678",
            "full_name": "Test Customer",
            "password": "securepass123",
        }

    def test_customer_registration_success(self):
        """A valid registration creates a user and returns 201."""
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["phone"], "01712345678")
        self.assertEqual(data["role"], "customer")
        self.assertFalse(data["is_phone_verified"])
        self.assertIn("id", data)

    def test_customer_registration_duplicate_phone(self):
        """Registering with an existing phone number returns 400."""
        self.client.post(self.url, self.valid_payload, format="json")
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_registration_invalid_phone(self):
        """Invalid phone format returns 400."""
        payload = {**self.valid_payload, "phone": "12345"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_registration_short_password(self):
        """Password shorter than 8 characters returns 400."""
        payload = {**self.valid_payload, "password": "short"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_registration_missing_fields(self):
        """Missing required fields return 400."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Error envelope check
        self.assertIn("error", response.json())


class PharmacyOwnerRegistrationTests(TestCase):
    """B1-02, B1-03: Pharmacy owner registration via API."""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/register/pharmacy-owner/"
        self.valid_payload = {
            "phone": "01798765432",
            "full_name": "Test Owner",
            "password": "ownerpass456",
        }

    def test_owner_registration_success(self):
        """A valid owner registration creates a user and returns 201."""
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["role"], "pharmacy_owner")
        self.assertFalse(data["is_phone_verified"])

    def test_owner_registration_duplicate_phone(self):
        """Registering with an existing phone returns 400."""
        self.client.post(self.url, self.valid_payload, format="json")
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(TestCase):
    """B1-03, B1-05: Login with JWT token issuance and throttling."""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/login/"
        self.user = User.objects.create_user(
            phone="01712345678",
            password="testpass123",
            full_name="Test User",
            role=User.Role.CUSTOMER,
        )

    def test_login_success(self):
        """Valid credentials return JWT access and refresh tokens."""
        payload = {"phone": "01712345678", "password": "testpass123"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["phone"], "01712345678")

    def test_login_wrong_password(self):
        """Wrong password returns 400."""
        payload = {"phone": "01712345678", "password": "wrongpass"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user(self):
        """Inactive user cannot log in."""
        self.user.is_active = False
        self.user.save()
        payload = {"phone": "01712345678", "password": "testpass123"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        """Missing phone or password returns 400."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_envelope_format(self):
        """Login errors use the standard error envelope."""
        payload = {"phone": "01712345678", "password": "wrong"}
        response = self.client.post(self.url, payload, format="json")
        body = response.json()
        self.assertIn("error", body)
        self.assertIn("code", body["error"])
        self.assertIn("message", body["error"])


class TokenRefreshTests(TestCase):
    """JWT token refresh flow."""

    def setUp(self):
        self.client = APIClient()
        self.login_url = "/api/v1/auth/login/"
        self.refresh_url = "/api/v1/auth/token/refresh/"
        self.user = User.objects.create_user(
            phone="01712345678",
            password="testpass123",
            full_name="Test User",
            role=User.Role.CUSTOMER,
        )
        login_response = self.client.post(
            self.login_url, {"phone": "01712345678", "password": "testpass123"}, format="json"
        )
        self.refresh_token = login_response.json()["refresh"]

    def test_token_refresh_success(self):
        """A valid refresh token returns a new access token."""
        payload = {"refresh": self.refresh_token}
        response = self.client.post(self.refresh_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())


class ProfileTests(TestCase):
    """B1-03: User profile retrieve and update."""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/profile/"
        self.user = User.objects.create_user(
            phone="01712345678",
            password="testpass123",
            full_name="Test User",
            role=User.Role.CUSTOMER,
        )

    def _auth(self):
        """Authenticate the test client as self.user."""
        from rest_framework_simplejwt.tokens import RefreshToken

        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

    def test_get_profile_authenticated(self):
        """Authenticated user can view their profile."""
        self._auth()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["phone"], "01712345678")

    def test_get_profile_unauthenticated(self):
        """Unauthenticated request returns 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        """Authenticated user can update their profile (partial)."""
        self._auth()
        response = self.client.patch(self.url, {"full_name": "Updated Name"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["full_name"], "Updated Name")

    def test_cannot_change_phone_through_profile(self):
        """Phone is read-only in profile endpoint."""
        self._auth()
        self.client.patch(self.url, {"phone": "01799999999"}, format="json")
        # Phone should remain unchanged (read-only field)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "01712345678")


class OTPSendTests(TestCase):
    """B1-12: OTP send endpoint — code generation, hashing, rate limiting."""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/otp/send/"
        self.phone = "01712345678"
        cache.clear()

    def test_otp_send_success(self):
        """Sending an OTP returns success and creates an OTPCode record."""
        response = self.client.post(self.url, {"phone": self.phone}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["phone"], self.phone)
        self.assertEqual(data["expires_in_minutes"], 10)

        # Verify OTPCode was created
        otp = OTPCode.objects.filter(phone=self.phone).first()
        self.assertIsNotNone(otp)
        self.assertFalse(otp.is_verified)
        self.assertIsNotNone(otp.expires_at)

    def test_otp_code_is_hashed(self):
        """OTP code is stored hashed, not in plaintext."""
        self.client.post(self.url, {"phone": self.phone}, format="json")
        otp = OTPCode.objects.filter(phone=self.phone).first()
        # The code field should not be a simple 6-digit string
        self.assertNotEqual(len(otp.code), 6)
        # It should be a valid Django hash (starts with algorithm prefix)
        self.assertTrue(otp.code.startswith(("pbkdf2_", "bcrypt", "argon2")) or len(otp.code) > 20)

    def test_otp_send_hashed_with_make_password(self):
        """Verify the stored hash can be verified with check_password."""
        self.client.post(self.url, {"phone": self.phone}, format="json")
        otp = OTPCode.objects.filter(phone=self.phone).first()
        # We don't know the plaintext, but we can verify the structure
        from django.contrib.auth.hashers import identify_hasher

        try:
            identify_hasher(otp.code)
            is_valid_hash = True
        except ValueError:
            is_valid_hash = False
        self.assertTrue(is_valid_hash, "OTP code must be a valid Django password hash")

    @patch("accounts.sms.console.ConsoleSmsSender.send_sms")
    def test_console_sms_sender_called(self, mock_send):
        """The SMS sender is called with the phone and a message containing the code."""
        response = self.client.post(self.url, {"phone": self.phone}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_send.called)
        call_args = mock_send.call_args
        self.assertEqual(call_args[0][0], self.phone)  # phone arg
        self.assertIn("verification code", call_args[0][1].lower())

    @patch("accounts.views.get_sms_sender")
    def test_otp_send_rate_limit(self, mock_get_sender):
        """Rate limit blocks after 5 requests per phone per hour."""
        mock_get_sender.return_value.send_sms.return_value = True

        # Send 5 requests (should all succeed)
        for i in range(5):
            response = self.client.post(self.url, {"phone": self.phone}, format="json")
            self.assertEqual(
                response.status_code, status.HTTP_200_OK,
                f"Request {i+1} should succeed",
            )

        # 6th request should be rate limited
        response = self.client.post(self.url, {"phone": self.phone}, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_otp_send_invalidates_previous(self):
        """Requesting a new OTP invalidates any prior unverified codes."""
        self.client.post(self.url, {"phone": self.phone}, format="json")
        first_code = OTPCode.objects.filter(phone=self.phone, is_verified=False).first()

        self.client.post(self.url, {"phone": self.phone}, format="json")
        # NOTE: "invalidate" means marking prior codes as is_verified=True.
        # This is semantically confusing but functionally correct — it ensures
        # the view's query (is_verified=False) only returns the newest code.
        first_code.refresh_from_db()
        self.assertTrue(first_code.is_verified)

    def test_otp_send_invalid_phone(self):
        """Invalid phone format returns 400."""
        response = self.client.post(self.url, {"phone": "123"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_otp_send_missing_phone(self):
        """Missing phone returns 400."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OTPVerifyTests(TestCase):
    """B1-13: OTP verify endpoint — success, wrong code, lockout, expiry."""

    def setUp(self):
        self.client = APIClient()
        self.send_url = "/api/v1/auth/otp/send/"
        self.verify_url = "/api/v1/auth/otp/verify/"
        self.phone = "01712345678"
        cache.clear()

    def _create_otp_with_code(self, phone, plain_code="123456",
                              expires_at=None):
        """Helper to create an OTPCode with a known plaintext code.

        Invalidates any existing unverified OTPs for the same phone first
        to avoid interference between tests.
        """
        from django.contrib.auth.hashers import make_password

        # Invalidate any prior unverified codes for this phone so the view
        # query (``expires_at__gt=now(), is_verified=False``) finds ours.
        OTPCode.objects.filter(phone=phone, is_verified=False).update(is_verified=True)

        if expires_at is None:
            expires_at = timezone.now() + timedelta(minutes=10)

        return OTPCode.objects.create(
            phone=phone,
            code=make_password(plain_code),
            expires_at=expires_at,
        )

    def test_otp_verify_success(self):
        """Valid code verifies successfully."""
        otp = self._create_otp_with_code(self.phone, "123456")
        payload = {"phone": self.phone, "code": "123456"}
        response = self.client.post(self.verify_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data["is_phone_verified"])

        # OTPCode should be marked as verified
        otp.refresh_from_db()
        self.assertTrue(otp.is_verified)

        # User should have phone_verified=True
        user = User.objects.filter(phone=self.phone).first()
        if user:
            self.assertTrue(user.is_phone_verified)

    def test_otp_verify_wrong_code(self):
        """Wrong code increments attempts and returns 400."""
        otp = self._create_otp_with_code(self.phone, "123456")
        payload = {"phone": self.phone, "code": "000000"}
        response = self.client.post(self.verify_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.json()
        self.assertIn("error", body)
        self.assertIn("attempt", body["error"]["message"].lower())

        otp.refresh_from_db()
        self.assertEqual(otp.attempts, 1)

    def test_otp_verify_lockout_after_5_failures(self):
        """After 5 failed attempts, the code is locked and user is prompted to request a new one."""
        self._create_otp_with_code(self.phone, "123456")

        # 5 failed attempts
        payload = {"phone": self.phone, "code": "000000"}
        for i in range(5):
            response = self.client.post(self.verify_url, payload, format="json")
            # First 5 should all be 400
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 6th attempt should also be 400, but message should say "Too many incorrect attempts"
        response = self.client.post(self.verify_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("too many", response.json()["error"]["message"].lower())

    def test_otp_verify_expired_code(self):
        """Expired OTP code is rejected."""
        otp = self._create_otp_with_code(self.phone, "123456")
        # Set expiry in the past
        otp.expires_at = timezone.now() - timedelta(minutes=1)
        otp.save()

        payload = {"phone": self.phone, "code": "123456"}
        response = self.client.post(self.verify_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no valid", response.json()["error"]["message"].lower())

    def test_otp_verify_no_code_exists(self):
        """Verifying with a phone that has no OTP returns 400."""
        payload = {"phone": "01999999999", "code": "123456"}
        response = self.client.post(self.verify_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_otp_verify_invalid_format(self):
        """Non-numeric or short code returns 400."""
        payload = {"phone": self.phone, "code": "abc"}
        response = self.client.post(self.verify_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_otp_verify_sets_phone_verified_on_user(self):
        """On successful OTP verification, the User's is_phone_verified flag is set."""
        # First create a user for this phone
        User.objects.create_user(
            phone=self.phone,
            password="testpass123",
            full_name="Verified User",
            role=User.Role.CUSTOMER,
        )

        self._create_otp_with_code(self.phone, "123456")
        payload = {"phone": self.phone, "code": "123456"}
        response = self.client.post(self.verify_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(phone=self.phone)
        self.assertTrue(user.is_phone_verified)
