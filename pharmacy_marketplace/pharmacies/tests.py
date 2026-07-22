"""
Comprehensive tests for the pharmacies app: Pharmacy model, CRUD operations,
geolocation updates, deactivation, and operating hours validation.
"""


from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from pharmacies.models import Pharmacy
from pharmacies.validators import validate_operating_hours


class PharmacyModelTests(TestCase):
    """B1-06: Pharmacy model structure and constraints."""

    def setUp(self):
        self.owner = User.objects.create_user(
            phone="01712345678",
            password="testpass123",
            full_name="Pharmacy Owner",
            role=User.Role.PHARMACY_OWNER,
        )

    def test_create_pharmacy(self):
        """A pharmacy can be created with all required fields."""
        pharmacy = Pharmacy.objects.create(
            owner=self.owner,
            name="Test Pharmacy",
            address_line="123 Main Road",
            city="Dhaka",
            division="Dhaka Division",
            location=Point(90.4125, 23.8103),
            phone="01711111111",
        )
        self.assertEqual(pharmacy.name, "Test Pharmacy")
        self.assertEqual(pharmacy.status, Pharmacy.Status.ACTIVE)
        self.assertFalse(pharmacy.is_verified)
        self.assertIsNotNone(pharmacy.location)

    def test_pharmacy_str(self):
        """String representation includes name and location."""
        pharmacy = Pharmacy.objects.create(
            owner=self.owner,
            name="Test Pharmacy",
            address_line="123 Main Road",
            city="Dhaka",
            division="Dhaka Division",
            location=Point(90.4125, 23.8103),
            phone="01711111111",
        )
        self.assertIn("Test Pharmacy", str(pharmacy))
        self.assertIn("Dhaka", str(pharmacy))

    def test_pharmacy_location_is_geography(self):
        """The location field should be a Point with SRID 4326."""
        pharmacy = Pharmacy.objects.create(
            owner=self.owner,
            name="Test Pharmacy",
            address_line="123 Main Road",
            city="Dhaka",
            division="Dhaka Division",
            location=Point(90.4125, 23.8103, srid=4326),
            phone="01711111111",
        )
        self.assertEqual(pharmacy.location.srid, 4326)
        self.assertEqual(pharmacy.location.x, 90.4125)
        self.assertEqual(pharmacy.location.y, 23.8103)

    def test_pharmacy_is_verified_default_false(self):
        """New pharmacies start as unverified."""
        pharmacy = Pharmacy.objects.create(
            owner=self.owner,
            name="Test Pharmacy",
            address_line="123 Main Road",
            city="Dhaka",
            division="Dhaka Division",
            location=Point(90.4125, 23.8103),
            phone="01711111111",
        )
        self.assertFalse(pharmacy.is_verified)

    def test_pharmacy_status_default_active(self):
        """New pharmacies start as active."""
        pharmacy = Pharmacy.objects.create(
            owner=self.owner,
            name="Test Pharmacy",
            address_line="123 Main Road",
            city="Dhaka",
            division="Dhaka Division",
            location=Point(90.4125, 23.8103),
            phone="01711111111",
        )
        self.assertEqual(pharmacy.status, Pharmacy.Status.ACTIVE)

    def test_pharmacy_dgda_license_optional(self):
        """DGDA license number is optional."""
        pharmacy = Pharmacy.objects.create(
            owner=self.owner,
            name="Test Pharmacy",
            address_line="123 Main Road",
            city="Dhaka",
            division="Dhaka Division",
            location=Point(90.4125, 23.8103),
            phone="01711111111",
        )
        self.assertEqual(pharmacy.dgda_license_number, "")


class OperatingHoursValidationTests(TestCase):
    """B1-06 acceptance criterion: operating_hours JSON validation."""

    def test_valid_hours_pass(self):
        """Valid operating hours structure passes validation."""
        value = {
            "mon": {"open": "09:00", "close": "21:00"},
            "tue": {"open": "09:00", "close": "21:00"},
            "wed": {"open": "09:00", "close": "21:00"},
            "thu": {"open": "09:00", "close": "21:00"},
            "fri": {"open": "14:00", "close": "21:00"},
            "sat": {"open": "09:00", "close": "22:00"},
            "sun": {"open": "10:00", "close": "18:00"},
        }
        # Should not raise
        validate_operating_hours(value)

    def test_none_passes(self):
        """None value passes validation (no hours set)."""
        validate_operating_hours(None)

    def test_empty_dict_passes(self):
        """Empty dict passes validation (no open days)."""
        validate_operating_hours({})

    def test_partial_week_passes(self):
        """Only some days present passes validation."""
        validate_operating_hours({"mon": {"open": "09:00", "close": "17:00"}})

    def test_invalid_day_key_fails(self):
        """Invalid day key raises ValidationError."""
        with self.assertRaises(Exception):
            validate_operating_hours({"monday": {"open": "09:00", "close": "17:00"}})

    def test_open_after_close_fails(self):
        """Open time after close time raises ValidationError."""
        with self.assertRaises(Exception):
            validate_operating_hours({"mon": {"open": "18:00", "close": "09:00"}})

    def test_open_equals_close_fails(self):
        """Open time equal to close time raises ValidationError."""
        with self.assertRaises(Exception):
            validate_operating_hours({"mon": {"open": "09:00", "close": "09:00"}})

    def test_invalid_time_format_fails(self):
        """Non-HH:MM time format raises ValidationError."""
        with self.assertRaises(Exception):
            validate_operating_hours({"mon": {"open": "9 AM", "close": "5 PM"}})

    def test_missing_open_key_fails(self):
        """Missing 'open' key raises ValidationError."""
        with self.assertRaises(Exception):
            validate_operating_hours({"mon": {"close": "17:00"}})

    def test_null_day_passes(self):
        """A day with null schedule passes (day is closed)."""
        validate_operating_hours({"mon": None, "tue": {"open": "09:00", "close": "17:00"}})

    def test_not_a_dict_fails(self):
        """Non-dict value raises ValidationError."""
        with self.assertRaises(Exception):
            validate_operating_hours("not a dict")

    def test_invalid_schedule_type_fails(self):
        """Schedule that is not a dict raises ValidationError."""
        with self.assertRaises(Exception):
            validate_operating_hours({"mon": "open-close"})


class PharmacyCRUDTests(TestCase):
    """B1-08: Pharmacy CRUD views (create, detail, update, deactivate)."""

    def setUp(self):
        self.owner = User.objects.create_user(
            phone="01712345678",
            password="testpass123",
            full_name="Pharmacy Owner",
            role=User.Role.PHARMACY_OWNER,
        )
        self.customer = User.objects.create_user(
            phone="01799999999",
            password="testpass123",
            full_name="Regular Customer",
            role=User.Role.CUSTOMER,
        )
        self.client = APIClient()

    def _auth_as(self, user):
        """Authenticate as the given user."""
        from rest_framework_simplejwt.tokens import RefreshToken

        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

    def _create_pharmacy_payload(self, **overrides):
        payload = {
            "name": "Test Pharmacy",
            "address_line": "123 Main Road",
            "city": "Dhaka",
            "division": "Dhaka Division",
            "location": {"type": "Point", "coordinates": [90.4125, 23.8103]},
            "phone": "01711111111",
        }
        payload.update(overrides)
        return payload

    def test_pharmacy_create_owner(self):
        """Pharmacy owner can create a pharmacy."""
        self._auth_as(self.owner)
        url = "/api/v1/pharmacies/"
        payload = self._create_pharmacy_payload()
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_pharmacy_create_unauthenticated(self):
        """Unauthenticated user cannot create a pharmacy."""
        url = "/api/v1/pharmacies/"
        payload = self._create_pharmacy_payload()
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pharmacy_create_customer_forbidden(self):
        """Customer user cannot create a pharmacy."""
        self._auth_as(self.customer)
        url = "/api/v1/pharmacies/"
        payload = self._create_pharmacy_payload()
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pharmacy_detail_public(self):
        """Pharmacy detail is publicly accessible."""
        pharmacy = Pharmacy.objects.create(
            owner=self.owner,
            name="Test Pharmacy",
            address_line="123 Main Road",
            city="Dhaka",
            division="Dhaka Division",
            location=Point(90.4125, 23.8103),
            phone="01711111111",
        )
        response = self.client.get(f"/api/v1/pharmacies/{pharmacy.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "Test Pharmacy")

    def test_pharmacy_update_owner(self):
        """Pharmacy owner can update their pharmacy."""
        pharmacy = Pharmacy.objects.create(
            owner=self.owner,
            name="Test Pharmacy",
            address_line="123 Main Road",
            city="Dhaka",
            division="Dhaka Division",
            location=Point(90.4125, 23.8103),
            phone="01711111111",
        )
        self._auth_as(self.owner)
        response = self.client.patch(
            f"/api/v1/pharmacies/{pharmacy.id}/",
            {"name": "Updated Pharmacy"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pharmacy.refresh_from_db()
        self.assertEqual(pharmacy.name, "Updated Pharmacy")

    def test_pharmacy_update_other_owner_forbidden(self):
        """Owner A cannot update Owner B's pharmacy."""
        other_owner = User.objects.create_user(
            phone="01722222222",
            password="testpass123",
            full_name="Other Owner",
            role=User.Role.PHARMACY_OWNER,
        )
        pharmacy = Pharmacy.objects.create(
            owner=self.owner,
            name="Test Pharmacy",
            address_line="123 Main Road",
            city="Dhaka",
            division="Dhaka Division",
            location=Point(90.4125, 23.8103),
            phone="01711111111",
        )
        self._auth_as(other_owner)
        response = self.client.patch(
            f"/api/v1/pharmacies/{pharmacy.id}/",
            {"name": "Hacked Name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pharmacy_deactivate(self):
        """Pharmacy owner can deactivate their pharmacy."""
        pharmacy = Pharmacy.objects.create(
            owner=self.owner,
            name="Test Pharmacy",
            address_line="123 Main Road",
            city="Dhaka",
            division="Dhaka Division",
            location=Point(90.4125, 23.8103),
            phone="01711111111",
        )
        self._auth_as(self.owner)
        response = self.client.patch(f"/api/v1/pharmacies/{pharmacy.id}/deactivate/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pharmacy.refresh_from_db()
        self.assertEqual(pharmacy.status, Pharmacy.Status.SUSPENDED)

    def test_pharmacy_location_update(self):
        """Pharmacy owner can update their geolocation."""
        pharmacy = Pharmacy.objects.create(
            owner=self.owner,
            name="Test Pharmacy",
            address_line="123 Main Road",
            city="Dhaka",
            division="Dhaka Division",
            location=Point(90.4125, 23.8103),
            phone="01711111111",
        )
        self._auth_as(self.owner)
        new_location = {"type": "Point", "coordinates": [90.5000, 23.9000]}
        response = self.client.patch(
            f"/api/v1/pharmacies/{pharmacy.id}/location/",
            {"location": new_location},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pharmacy.refresh_from_db()
        self.assertAlmostEqual(pharmacy.location.x, 90.5000)
        self.assertAlmostEqual(pharmacy.location.y, 23.9000)
