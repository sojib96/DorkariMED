"""
Accounts app — User model with phone-based authentication.

Single User model with a role field (customer / pharmacy_owner / admin),
phone as the unique identifier, and SMS OTP verification support.
"""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager for User model — uses phone as the unique identifier."""

    def create_user(self, phone, password=None, **extra_fields):
        """Create and return a regular user with the given phone and password."""
        if not phone:
            raise ValueError("The phone number must be set")
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "customer")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """Create and return a superuser (admin role) with the given phone and password."""
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("role") != "admin":
            raise ValueError("Superuser must have role='admin'.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using phone number as the unique identifier.

    Single table with a ``role`` field for authorization boundaries.
    Email is optional (nullable) — used only for account recovery,
    never for OTP or primary auth.
    """

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        PHARMACY_OWNER = "pharmacy_owner", "Pharmacy Owner"
        ADMIN = "admin", "Admin"

    phone = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Bangladeshi phone number (e.g., 01712345678)",
    )
    email = models.EmailField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Optional — used only for account recovery, never for OTP",
    )
    full_name = models.CharField(
        max_length=255,
        help_text="Full name as displayed across the platform",
    )
    role = models.CharField(
        max_length=20,
        choices=Role,
        default=Role.CUSTOMER,
        db_index=True,
        help_text="Authorization role: customer, pharmacy_owner, or admin",
    )
    default_latitude = models.FloatField(
        null=True,
        blank=True,
        help_text="Saved home latitude for default discovery radius",
    )
    default_longitude = models.FloatField(
        null=True,
        blank=True,
        help_text="Saved home longitude for default discovery radius",
    )
    is_phone_verified = models.BooleanField(
        default=False,
        help_text="Has the user completed SMS OTP verification?",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this user active? Unselect instead of deleting accounts.",
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Can this user access the Django admin interface?",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["full_name", "role"]

    class Meta:
        db_table = "accounts_user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["is_phone_verified"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


class OTPCode(models.Model):
    """
    One-time password code for SMS phone verification.

    Codes are stored hashed (via Django's ``make_password``), not in
    plaintext. Each phone number can have at most one active (unverified,
    non-expired) OTP code at a time — requesting a new one invalidates
    the previous.
    """

    phone = models.CharField(
        max_length=20,
        db_index=True,
        help_text="Phone number this code was sent to",
    )
    code = models.CharField(
        max_length=128,
        help_text="Hashed OTP code (stored via Django's make_password, never plaintext)",
    )
    attempts = models.IntegerField(
        default=0,
        help_text="Number of failed verification attempts",
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Has this code been successfully verified?",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="Code is invalid after this timestamp (set to now + 10 minutes)",
    )

    class Meta:
        db_table = "accounts_otp_code"
        verbose_name = "OTP Code"
        verbose_name_plural = "OTP Codes"
        indexes = [
            models.Index(fields=["phone", "is_verified", "expires_at"]),
        ]

    def __str__(self):
        return f"OTP for {self.phone} (verified={self.is_verified})"
