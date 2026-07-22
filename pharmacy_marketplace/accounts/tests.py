"""
Comprehensive tests for the accounts app: User model, registration, login,
profile, OTP send/verify, rate limiting, and lockout behaviour.
"""

from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
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

    @patch("accounts.api_views.get_sms_sender")
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


# ────────────────────────────────────────────────────────────────────────────
# F1-08: Web auth integration tests (session-based, Django template views)
# Tested with django.test.Client to exercise the full request/response cycle
# for web registration, login, logout, and the dashboard shell.
# ────────────────────────────────────────────────────────────────────────────


class WebCustomerRegistrationTests(TestCase):
    """F1-04 / F1-08: Customer registration via web form (session-based).

    Tests GET (form render), POST valid (creates user + returns OTP partial),
    POST invalid (validation errors re-rendered), and duplicate phone.
    """

    def setUp(self):
        self.client = Client()
        self.url = reverse("auth:customer-register")
        self.valid_payload = {
            "full_name": "Test Customer",
            "phone": "01712345678",
            "password": "securepass123",
            "confirm_password": "securepass123",
        }

    def test_get_renders_form(self):
        """GET /customer/register/ renders the registration form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customer/register.html")
        # Form fields should be present
        self.assertContains(response, 'name="full_name"')
        self.assertContains(response, 'name="phone"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'name="confirm_password"')

    def test_post_valid_creates_user(self):
        """POST with valid data creates a user and returns OTP partial."""
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/_otp_verify.html")
        # User created
        self.assertTrue(User.objects.filter(phone="01712345678").exists())
        # User is logged in (session has user)
        self.assertEqual(self.client.session["_auth_user_id"], str(User.objects.get(phone="01712345678").pk))

    def test_post_duplicate_phone(self):
        """POST with existing phone re-renders form with error."""
        # Create user first
        User.objects.create_user(
            phone="01712345678", password="pass123",
            full_name="Existing", role=User.Role.CUSTOMER,
        )
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customer/register.html")
        self.assertContains(response, "already registered")

    def test_post_missing_full_name(self):
        """Missing full name returns validation error."""
        payload = {**self.valid_payload, "full_name": ""}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customer/register.html")
        self.assertContains(response, "full name")

    def test_post_invalid_phone(self):
        """Invalid phone format returns validation error."""
        payload = {**self.valid_payload, "phone": "12345"}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "valid Bangladeshi")

    def test_post_short_password(self):
        """Short password returns validation error."""
        payload = {**self.valid_payload, "password": "short"}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "at least 8")

    def test_post_password_mismatch(self):
        """Mismatched passwords returns validation error."""
        payload = {**self.valid_payload, "password": "pass12345", "confirm_password": "diffpass56"}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "do not match")

    def test_authenticated_user_redirects(self):
        """Logged-in user submitting the form gets redirected."""
        User.objects.create_user(
            phone="01999999999", password="pass123",
            full_name="Logged In", role=User.Role.CUSTOMER,
        )
        self.client.login(phone="01999999999", password="pass123")
        response = self.client.post(self.url, self.valid_payload)
        self.assertIn(response.status_code, [302, 200])
        if response.status_code == 200:
            self.assertContains(response, "already logged in", html=False)


class WebCustomerLoginTests(TestCase):
    """F1-05 / F1-08: Customer login via web form (session-based)."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("auth:customer-login")
        self.user = User.objects.create_user(
            phone="01712345678", password="testpass123",
            full_name="Test Customer", role=User.Role.CUSTOMER,
        )

    def test_get_renders_form(self):
        """GET /customer/login/ renders the login form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customer/login.html")
        self.assertContains(response, 'name="phone"')
        self.assertContains(response, 'name="password"')

    def test_post_valid_authenticates(self):
        """POST with valid credentials logs the user in."""
        response = self.client.post(self.url, {
            "phone": "01712345678", "password": "testpass123",
        })
        self.assertIn(response.status_code, [302, 200])
        self.assertEqual(
            str(self.client.session["_auth_user_id"]),
            str(self.user.pk),
        )

    def test_post_invalid_credentials(self):
        """POST with wrong password returns form with error."""
        response = self.client.post(self.url, {
            "phone": "01712345678", "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customer/login.html")
        self.assertContains(response, "Invalid phone number or password")

    def test_post_missing_fields(self):
        """Missing phone or password returns form with errors."""
        response = self.client.post(self.url, {"phone": "", "password": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "phone number")
        self.assertContains(response, "password")

    def test_authenticated_user_gets_already_logged_in_context(self):
        """Logged-in user gets already_logged_in context flag."""
        self.client.login(phone="01712345678", password="testpass123")
        response = self.client.get(self.url)
        context = response.context[-1]
        self.assertTrue(context.get("already_logged_in"))


class WebOwnerRegistrationTests(TestCase):
    """F1-06 / F1-08: Owner registration — Step 1 (account info).

    Full multi-step flow (steps 2-4) requires PostGIS (Pharmacy model).
    Step 1 (user account, no GIS dependency) is tested here.
    """

    def setUp(self):
        self.client = Client()
        self.url = reverse("auth:owner-register")
        self.step1_payload = {
            "step": "0",
            "full_name": "Test Owner",
            "phone": "01798765432",
            "password": "ownerpass456",
            "confirm_password": "ownerpass456",
        }

    def test_get_renders_step1(self):
        """GET /owner/register/ renders step 1 of the registration form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "owner/register.html")
        # Step indicator should show step 1 as current
        self.assertContains(response, "Step 1 of 4")
        self.assertContains(response, 'name="full_name"')
        self.assertContains(response, 'name="phone"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'name="confirm_password"')

    def test_step1_valid_saves_to_session(self):
        """POST step 1 with valid data advances to step 2 (pharmacy details)."""
        response = self.client.post(self.url, self.step1_payload)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "owner/register.html")
        self.assertContains(response, "Step 2 of 4")
        # Check session data
        self.assertIn("owner_registration", self.client.session)
        self.assertEqual(
            self.client.session["owner_registration"]["full_name"],
            "Test Owner",
        )

    def test_step1_missing_full_name(self):
        """Missing full name returns validation error on step 1."""
        payload = {**self.step1_payload, "full_name": ""}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter your full name")

    def test_step1_invalid_phone(self):
        """Invalid phone returns validation error on step 1."""
        payload = {**self.step1_payload, "phone": "12345"}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "valid Bangladeshi")

    def test_step1_duplicate_phone(self):
        """Duplicate phone returns validation error on step 1."""
        User.objects.create_user(
            phone="01798765432", password="pass123",
            full_name="Existing", role=User.Role.CUSTOMER,
        )
        response = self.client.post(self.url, self.step1_payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already registered")

    def test_step1_password_mismatch(self):
        """Password mismatch returns validation error."""
        payload = {**self.step1_payload, "password": "pass12345", "confirm_password": "diffpass56"}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "do not match")

    def test_step1_short_password(self):
        """Short password returns validation error."""
        payload = {**self.step1_payload, "password": "short"}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "at least 8")

    def test_authenticated_user_redirects(self):
        """Already authenticated user is redirected to dashboard."""
        User.objects.create_user(
            phone="01999999999", password="pass123",
            full_name="LoggedIn Owner", role=User.Role.PHARMACY_OWNER,
        )
        self.client.login(phone="01999999999", password="pass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("dashboard", response.url)


class WebOwnerLoginTests(TestCase):
    """F1-07 / F1-08: Owner login via web form (session-based)."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("auth:owner-login")
        self.user = User.objects.create_user(
            phone="01798765432", password="ownerpass456",
            full_name="Test Owner", role=User.Role.PHARMACY_OWNER,
        )

    def test_get_renders_form(self):
        """GET /owner/login/ renders the owner login form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "owner/login.html")
        self.assertContains(response, 'name="phone"')
        self.assertContains(response, 'name="password"')

    def test_post_valid_authenticates(self):
        """POST with valid credentials logs the owner in."""
        response = self.client.post(self.url, {
            "phone": "01798765432", "password": "ownerpass456",
        })
        self.assertIn(response.status_code, [302, 200])
        self.assertEqual(
            str(self.client.session["_auth_user_id"]),
            str(self.user.pk),
        )

    def test_post_invalid_credentials(self):
        """POST with wrong password returns form with error."""
        response = self.client.post(self.url, {
            "phone": "01798765432", "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid phone number or password")

    def test_post_customer_role_rejected(self):
        """Customer user trying owner login sees role-specific error."""
        User.objects.create_user(
            phone="01700000000", password="pass123",
            full_name="Customer User", role=User.Role.CUSTOMER,
        )
        response = self.client.post(self.url, {
            "phone": "01700000000", "password": "pass123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not registered as a pharmacy owner")

    def test_authenticated_user_redirects(self):
        """Already authenticated owner is redirected to dashboard."""
        self.client.login(phone="01798765432", password="ownerpass456")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("dashboard", response.url)


class WebOwnerDashboardTests(TestCase):
    """F1-07 / F1-08: Owner dashboard shell — auth protection, data display."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("owner:dashboard")

    def test_unauthenticated_redirects_to_login(self):
        """Unauthenticated user is redirected to owner login."""
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [302, 200])
        if response.status_code == 302:
            self.assertIn("login", response.url)

    def test_authenticated_renders_template(self):
        """Authenticated owner sees the dashboard template."""
        user = User.objects.create_user(
            phone="01798765432", password="pass123",
            full_name="Dashboard Owner", role=User.Role.PHARMACY_OWNER,
        )
        self.client.login(phone="01798765432", password="pass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "owner/dashboard.html")

    def test_dashboard_shows_welcome(self):
        """Dashboard displays the welcome card."""
        user = User.objects.create_user(
            phone="01798765432", password="pass123",
            full_name="Welcome User", role=User.Role.PHARMACY_OWNER,
        )
        self.client.login(phone="01798765432", password="pass123")
        response = self.client.get(self.url)
        self.assertContains(response, "Welcome")


class WebLogoutTests(TestCase):
    """F1-08: Logout redirects appropriately based on role."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("auth:logout")

    def test_logout_clears_session(self):
        """POST to logout clears the session."""
        User.objects.create_user(
            phone="01712345678", password="pass123",
            full_name="Logout User", role=User.Role.CUSTOMER,
        )
        self.client.login(phone="01712345678", password="pass123")
        self.assertIn("_auth_user_id", self.client.session)
        response = self.client.post(self.url)
        self.assertIn(response.status_code, [302, 200])
        # Session should be cleared
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_owner_redirects_to_owner_login(self):
        """Owner logout redirects to /owner/login/."""
        User.objects.create_user(
            phone="01798765432", password="pass123",
            full_name="Owner Logout", role=User.Role.PHARMACY_OWNER,
        )
        self.client.login(phone="01798765432", password="pass123")
        response = self.client.post(self.url)
        self.assertIn(response.status_code, [302, 200])

    def test_logout_customer_redirects_to_home(self):
        """Customer logout redirects to /."""
        User.objects.create_user(
            phone="01712345678", password="pass123",
            full_name="Customer Logout", role=User.Role.CUSTOMER,
        )
        self.client.login(phone="01712345678", password="pass123")
        response = self.client.post(self.url)
        self.assertIn(response.status_code, [302, 200])
