from django.contrib.gis.db import models as gis_models
from django.db import models

from core.models import BaseModel


class Pharmacy(BaseModel):
    """
    Pharmacy storefront registered on the platform.

    Each pharmacy has a location (PostGIS Point), contact details,
    operational hours, and an owner (User with is_pharmacy_owner=True).
    """

    owner = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="pharmacies",
        help_text="User who manages this pharmacy storefront",
    )
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly identifier")
    address = models.TextField()
    location = gis_models.PointField(
        srid=4326,
        geography=True,
        help_text="Geographic coordinates (longitude, latitude) — PostGIS GEOGRAPHY point",
    )
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Operational details
    license_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="DGDA pharmacy license number",
    )
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    is_open_on_sunday = models.BooleanField(default=True)
    is_open_on_saturday = models.BooleanField(default=False)

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Is this pharmacy visible and accepting discovery requests?",
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Has the pharmacy's license been verified by platform admin?",
    )

    # Photo / branding
    photo = models.ImageField(upload_to="pharmacy_photos/", blank=True)

    class Meta:
        db_table = "pharmacies_pharmacy"
        verbose_name = "Pharmacy"
        verbose_name_plural = "Pharmacies"
        indexes = [
            models.Index(fields=["is_active", "is_verified"]),
        ]

    def __str__(self):
        return self.name
