"""
Pharmacies app serializers — pharmacy CRUD and geolocation.

Includes operating_hours JSON validation using the custom validator
from ``pharmacies.validators``.
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from pharmacies.models import Pharmacy
from pharmacies.validators import validate_operating_hours


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
        """Ensure location has valid coordinates."""
        if value is None:
            raise serializers.ValidationError(_("Location is required."))
        return value


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
        if value is None:
            raise serializers.ValidationError(_("Location is required."))
        return value
