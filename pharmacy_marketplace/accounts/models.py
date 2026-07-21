from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with phone-number authentication support.

    Uses email as the username field for uniqueness but primary login
    is via phone + OTP. Email/password login is available as fallback
    for Django admin accounts.
    """

    phone = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        help_text="Bangladeshi phone number (e.g., 01712345678)",
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        help_text="Optional — used for recovery and admin access",
    )
    is_phone_verified = models.BooleanField(
        default=False,
        help_text="Has the user completed SMS OTP verification?",
    )
    is_pharmacy_owner = models.BooleanField(
        default=False,
        help_text="Can this user manage a pharmacy storefront?",
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "accounts_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.phone
