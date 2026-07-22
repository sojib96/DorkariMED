"""
Accounts app serializers — registration, login, profile, and OTP.

Pharmacy owner registration nests pharmacy data in the same payload
so that a single API call creates both the User and the Pharmacy.
"""

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from accounts.models import User


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """Register a customer account (phone, full_name, password)."""

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="Minimum 8 characters",
    )

    class Meta:
        model = User
        fields = ["phone", "full_name", "password"]

    def validate_phone(self, value):
        """Basic Bangladeshi phone format check."""
        if not value.startswith("01") or len(value) != 11 or not value.isdigit():
            raise serializers.ValidationError(
                _("Enter a valid Bangladeshi phone number (e.g., 01712345678).")
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.role = User.Role.CUSTOMER
        user.save()
        return user


class PharmacyOwnerRegistrationSerializer(serializers.ModelSerializer):
    """
    Register a pharmacy owner with nested pharmacy data.

    Expects ``pharmacy`` as a nested object inside the registration payload.
    The pharmacy is created after the user is saved.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["phone", "full_name", "password"]

    def validate_phone(self, value):
        if not value.startswith("01") or len(value) != 11 or not value.isdigit():
            raise serializers.ValidationError(
                _("Enter a valid Bangladeshi phone number (e.g., 01712345678).")
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.role = User.Role.PHARMACY_OWNER
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Authenticate a user by phone + password and return the user instance.

    Used by the LoginView to validate credentials before issuing a JWT.
    """

    phone = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, data):
        phone = data.get("phone")
        password = data.get("password")

        if phone and password:
            user = authenticate(phone=phone, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError(
                        _("This account is inactive."), code="account_inactive"
                    )
                data["user"] = user
            else:
                raise serializers.ValidationError(
                    _("Unable to log in with provided credentials."), code="invalid_credentials"
                )
        else:
            raise serializers.ValidationError(
                _("Both phone and password are required."), code="missing_fields"
            )
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Read/write serializer for the authenticated user's profile."""

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "full_name",
            "email",
            "role",
            "default_latitude",
            "default_longitude",
            "is_phone_verified",
            "created_at",
        ]
        read_only_fields = ["id", "phone", "role", "is_phone_verified", "created_at"]


class SendOtpSerializer(serializers.Serializer):
    """Initiate OTP sending to a phone number."""

    phone = serializers.CharField()

    def validate_phone(self, value):
        if not value.startswith("01") or len(value) != 11 or not value.isdigit():
            raise serializers.ValidationError(
                _("Enter a valid Bangladeshi phone number.")
            )
        return value


class VerifyOtpSerializer(serializers.Serializer):
    """Verify an OTP code submitted by the user."""

    phone = serializers.CharField()
    code = serializers.CharField(min_length=6, max_length=6)

    def validate_phone(self, value):
        if not value.startswith("01") or len(value) != 11 or not value.isdigit():
            raise serializers.ValidationError(
                _("Enter a valid Bangladeshi phone number.")
            )
        return value

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                _("OTP code must be a 6-digit number.")
            )
        return value
