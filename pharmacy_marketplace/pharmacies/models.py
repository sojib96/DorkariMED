"""
Pharmacies app — Pharmacy model with PostGIS geolocation.

Each pharmacy has a location (PostGIS GEOGRAPHY Point), operating hours
stored as JSON, and a status workflow (active / suspended / pending_review).
"""

from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.indexes import GistIndex
from django.db import models

from core.models import BaseModel


class Pharmacy(BaseModel):
    """
    Pharmacy storefront registered on the platform.

    The ``location`` field uses PostGIS GEOGRAPHY type (SRID 4326) for
    accurate sphere distance calculations via ``ST_DWithin``.

    ``operating_hours`` is a JSONField storing a structured schedule:
    ``{"mon": {"open": "09:00", "close": "21:00"}, "tue": {...}, ...}``
    Days with ``null`` or omitted are treated as closed.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        PENDING_REVIEW = "pending_review", "Pending Review"

    owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="pharmacies",
        help_text="User with role=pharmacy_owner who manages this storefront",
    )
    name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Pharmacy name as displayed to customers",
    )
    address_line = models.CharField(
        max_length=500,
        help_text="Street address line",
    )
    city = models.CharField(
        max_length=100,
        help_text="City (e.g., Dhaka, Chattogram)",
    )
    division = models.CharField(
        max_length=100,
        help_text="Administrative division (e.g., Dhaka Division)",
    )
    location = gis_models.PointField(
        srid=4326,
        geography=True,
        help_text="Pharmacy location as PostGIS GEOGRAPHY point (lng, lat)",
    )
    dgda_license_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="DGDA-issued pharmacy license number (captured but not verified in M1)",
    )
    pharmacist_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of the registered pharmacist on duty (Section 45 compliance)",
    )
    pharmacist_registration_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Pharmacy Council registration number of the supervising pharmacist",
    )
    operating_hours = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON schedule: {\"mon\": {\"open\": \"09:00\", \"close\": \"21:00\"}, ...}",
    )
    phone = models.CharField(
        max_length=20,
        help_text="Primary contact phone number",
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.ACTIVE,
        db_index=True,
        help_text="Storefront visibility status",
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Has the pharmacy's DGDA license been verified by platform admin?",
    )

    class Meta:
        db_table = "pharmacies_pharmacy"
        verbose_name = "Pharmacy"
        verbose_name_plural = "Pharmacies"
        indexes = [
            models.Index(fields=["status", "is_verified"]),
            GistIndex(fields=["location"], name="idx_pharmacy_location_gist"),
        ]

    def __str__(self):
        return f"{self.name} ({self.city}, {self.division})"
