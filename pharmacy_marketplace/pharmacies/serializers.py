"""
Pharmacies app serializers — pharmacy CRUD and geolocation.

Includes operating_hours JSON validation using the custom validator
from ``pharmacies.validators``.
"""

from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from pharmacies.models import Pharmacy
from pharmacies.validators import validate_operating_hours


def _coerce_location(value):
    """Convert a GeoJSON dict to a GEOS Point if needed.

    DRF passes the location value as a Python dict parsed from JSON
    (e.g. ``{"type": "Point", "coordinates": [90.4, 23.8]}``). GeoDjango's
    SpatialProxy rejects raw dicts, so we convert to a ``Point`` object
    before passing to ``create()`` / ``update()``.
    """
    if value is not None and isinstance(value, dict):
        try:
            return Point(value["coordinates"][0], value["coordinates"][1], srid=4326)
        except (KeyError, TypeError, IndexError):
            raise serializers.ValidationError(
                _("Location must be a GeoJSON Point: "
                  "{\"type\": \"Point\", \"coordinates\": [lng, lat]}.")
            )
    return value


class PharmacyRegistrationSerializer(serializers.ModelSerializer):
    """
    Create a pharmacy profile (used nested inside owner registration).

    This serializer is used when a pharmacy owner registers: the owner
    registration endpoint receives pharmacy data alongside user data.
    """

    class Meta:
        model = Pharmacy
        fields = [
            "name",
            "address_line",
            "city",
            "division",
            "location",
            "dgda_license_number",
            "pharmacist_name",
            "pharmacist_registration_number",
            "operating_hours",
            "phone",
        ]

    def validate_operating_hours(self, value):
        validate_operating_hours(value)
        return value

    def validate_location(self, value):
        """Ensure location is valid and convert GeoJSON dict to a Point object."""
        if value is None:
            raise serializers.ValidationError(_("Location is required."))
        return _coerce_location(value)


class PharmacyDetailSerializer(serializers.ModelSerializer):
    """
    Public pharmacy storefront — no sensitive fields.

    Returned when a customer views a pharmacy's storefront.
    """

    owner_name = serializers.CharField(source="owner.full_name", read_only=True)
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = Pharmacy
        fields = [
            "id",
            "name",
            "owner_name",
            "address_line",
            "city",
            "division",
            "location",
            "phone",
            "operating_hours",
            "status",
            "is_verified",
            "distance_km",
            "created_at",
        ]
        read_only_fields = ["id", "status", "is_verified", "created_at"]

    def get_distance_km(self, obj):
        """
        Return distance if a ``_distance_km`` annotation is present
        (set by the search endpoint's PostGIS query). Returns ``None``
        when not in a radius query context.
        """
        return getattr(obj, "_distance_km", None)


class PharmacyUpdateSerializer(serializers.ModelSerializer):
    """Update pharmacy profile (owner-only)."""

    class Meta:
        model = Pharmacy
        fields = [
            "name",
            "address_line",
            "city",
            "division",
            "dgda_license_number",
            "pharmacist_name",
            "pharmacist_registration_number",
            "operating_hours",
            "phone",
        ]

    def validate_operating_hours(self, value):
        validate_operating_hours(value)
        return value


class PharmacyLocationSerializer(serializers.ModelSerializer):
    """Update only the geolocation pin."""

    class Meta:
        model = Pharmacy
        fields = ["location"]

    def validate_location(self, value):
        """Ensure location is valid and convert GeoJSON dict to a Point object."""
        if value is None:
            raise serializers.ValidationError(_("Location is required."))
        return _coerce_location(value)
