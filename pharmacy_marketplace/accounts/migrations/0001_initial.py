# Generated manually for Phase 1 (GDAL not available on dev machine).
# Creates the custom User model (AbstractBaseUser + PermissionsMixin with role field)
# and the OTPCode model for SMS phone verification.

import django.contrib.auth.password_validation
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        # ── User model ─────────────────────────────────────────────────────
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        db_index=True,
                        help_text="Bangladeshi phone number (e.g., 01712345678)",
                        max_length=20,
                        unique=True,
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        db_index=True,
                        help_text="Optional — used only for account recovery, never for OTP",
                        max_length=254,
                        null=True,
                    ),
                ),
                (
                    "full_name",
                    models.CharField(
                        help_text="Full name as displayed across the platform",
                        max_length=255,
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[("customer", "Customer"), ("pharmacy_owner", "Pharmacy Owner"), ("admin", "Admin")],
                        db_index=True,
                        default="customer",
                        help_text="Authorization role: customer, pharmacy_owner, or admin",
                        max_length=20,
                    ),
                ),
                (
                    "default_latitude",
                    models.FloatField(
                        blank=True,
                        help_text="Saved home latitude for default discovery radius",
                        null=True,
                    ),
                ),
                (
                    "default_longitude",
                    models.FloatField(
                        blank=True,
                        help_text="Saved home longitude for default discovery radius",
                        null=True,
                    ),
                ),
                (
                    "is_phone_verified",
                    models.BooleanField(
                        default=False,
                        help_text="Has the user completed SMS OTP verification?",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Is this user active? Unselect instead of deleting accounts.",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Can this user access the Django admin interface?",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "db_table": "accounts_user",
                "verbose_name": "User",
                "verbose_name_plural": "Users",
                "indexes": [
                    models.Index(fields=["role"], name="accounts_user_role_idx"),
                    models.Index(fields=["is_phone_verified"], name="accounts_user_phone_verified_idx"),
                ],
            },
            managers=[],
        ),
        # ── OTPCode model ──────────────────────────────────────────────────
        migrations.CreateModel(
            name="OTPCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "phone",
                    models.CharField(
                        db_index=True,
                        help_text="Phone number this code was sent to",
                        max_length=20,
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        help_text="Hashed OTP code (stored via Django's make_password, never plaintext)",
                        max_length=128,
                    ),
                ),
                ("attempts", models.IntegerField(default=0, help_text="Number of failed verification attempts")),
                (
                    "is_verified",
                    models.BooleanField(default=False, help_text="Has this code been successfully verified?"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "expires_at",
                    models.DateTimeField(
                        help_text="Code is invalid after this timestamp (set to now + 10 minutes)"
                    ),
                ),
            ],
            options={
                "db_table": "accounts_otp_code",
                "verbose_name": "OTP Code",
                "verbose_name_plural": "OTP Codes",
                "indexes": [
                    models.Index(fields=["phone", "is_verified", "expires_at"], name="otp_lookup_idx"),
                ],
            },
        ),
    ]
