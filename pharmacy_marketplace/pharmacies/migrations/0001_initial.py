# Generated manually for Phase 1 (GDAL not available on dev machine).
# Creates the Pharmacy model with PostGIS GEOGRAPHY PointField and GIST index.

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.contrib.postgres.indexes import GistIndex
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Pharmacy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(db_index=True, help_text="Pharmacy name as displayed to customers", max_length=255),
                ),
                ("address_line", models.CharField(help_text="Street address line", max_length=500)),
                ("city", models.CharField(help_text="City (e.g., Dhaka, Chattogram)", max_length=100)),
                ("division", models.CharField(help_text="Administrative division (e.g., Dhaka Division)", max_length=100)),
                (
                    "location",
                    django.contrib.gis.db.models.fields.PointField(
                        geography=True,
                        help_text="Pharmacy location as PostGIS GEOGRAPHY point (lng, lat)",
                        srid=4326,
                    ),
                ),
                (
                    "dgda_license_number",
                    models.CharField(
                        blank=True,
                        help_text="DGDA-issued pharmacy license number (captured but not verified in M1)",
                        max_length=100,
                    ),
                ),
                (
                    "pharmacist_name",
                    models.CharField(
                        blank=True,
                        help_text="Name of the registered pharmacist on duty (Section 45 compliance)",
                        max_length=255,
                    ),
                ),
                (
                    "pharmacist_registration_number",
                    models.CharField(
                        blank=True,
                        help_text="Pharmacy Council registration number of the supervising pharmacist",
                        max_length=100,
                    ),
                ),
                (
                    "operating_hours",
                    models.JSONField(
                        blank=True,
                        help_text='JSON schedule: {"mon": {"open": "09:00", "close": "21:00"}, ...}',
                        null=True,
                    ),
                ),
                ("phone", models.CharField(help_text="Primary contact phone number", max_length=20)),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("suspended", "Suspended"), ("pending_review", "Pending Review")],
                        db_index=True,
                        default="active",
                        help_text="Storefront visibility status",
                        max_length=20,
                    ),
                ),
                (
                    "is_verified",
                    models.BooleanField(
                        default=False,
                        help_text="Has the pharmacy's DGDA license been verified by platform admin?",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        help_text="User with role=pharmacy_owner who manages this storefront",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pharmacies",
                        to="accounts.user",
                    ),
                ),
            ],
            options={
                "db_table": "pharmacies_pharmacy",
                "verbose_name": "Pharmacy",
                "verbose_name_plural": "Pharmacies",
                "indexes": [
                    models.Index(fields=["status", "is_verified"], name="pharm_status_verified_idx"),
                    GistIndex(fields=["location"], name="idx_pharmacy_location_gist"),
                ],
            },
        ),
    ]
