from django.core.validators import MinValueValidator
from django.db import models

from core.models import BaseModel


class MasterMedicine(BaseModel):
    """
    Canonical medicine catalog curated by platform admin.

    Represents known medicines with standard names, generic equivalents,
    and dosage forms. PharmacyMedicineListing entries with a matching
    master_medicine_id reference this table for normalized search.
    """

    generic_name = models.CharField(
        max_length=300,
        db_index=True,
        help_text="Generic / INN name (e.g., Paracetamol)",
    )
    brand_name = models.CharField(
        max_length=300,
        blank=True,
        help_text="Brand/trade name if different from generic",
    )
    dosage_form = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., Tablet, Syrup, Injection, Cream",
    )
    strength = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., 500mg, 250mg/5ml",
    )
    manufacturer = models.CharField(
        max_length=300,
        blank=True,
        help_text="Manufacturer company name",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this entry available for pharmacy listings?",
    )

    class Meta:
        db_table = "catalog_master_medicine"
        verbose_name = "Master Medicine"
        verbose_name_plural = "Master Medicines"
        indexes = [
            models.Index(fields=["generic_name", "brand_name"]),
        ]

    def __str__(self):
        return f"{self.brand_name or self.generic_name} ({self.strength})"


class PharmacyMedicineListing(BaseModel):
    """
    Pivot entity: a pharmacy's specific offering of a medicine.

    This is THE most structurally important model in Module 1.
    Future OrderItem will reference this, not MasterMedicine.

    For known medicines, master_medicine_id links to the curated catalog.
    For unknown medicines, the pharmacy provides free-text fields as fallback.
    Admin normalizes free-text entries by setting master_medicine_id later.
    """

    pharmacy = models.ForeignKey(
        "pharmacies.Pharmacy",
        on_delete=models.CASCADE,
        related_name="medicine_listings",
        help_text="The pharmacy offering this medicine",
    )
    master_medicine = models.ForeignKey(
        "catalog.MasterMedicine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pharmacy_listings",
        help_text="Canonical medicine entry (NULL until admin normalizes free-text entries)",
    )

    # ── Free-text fallback fields ──────────────────────────────────────────
    # Used when master_medicine_id is NULL (unlisted medicine).
    # Once admin sets master_medicine_id, these become denormalized copies
    # for search performance (avoids a join back to MasterMedicine).
    fallback_generic_name = models.CharField(max_length=300, blank=True)
    fallback_brand_name = models.CharField(max_length=300, blank=True)
    fallback_dosage_form = models.CharField(max_length=100, blank=True)
    fallback_strength = models.CharField(max_length=100, blank=True)
    fallback_manufacturer = models.CharField(max_length=300, blank=True)

    # ── Pricing & availability ─────────────────────────────────────────────
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Current selling price in BDT",
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Is this medicine currently in stock?",
    )
    notes = models.TextField(
        blank=True,
        help_text="Optional pharmacy-specific notes (e.g., 'generic available')",
    )

    class Meta:
        db_table = "catalog_pharmacy_medicine_listing"
        verbose_name = "Pharmacy Medicine Listing"
        verbose_name_plural = "Pharmacy Medicine Listings"
        constraints = [
            models.UniqueConstraint(
                fields=["pharmacy", "master_medicine"],
                name="uq_pharmacy_master_medicine",
                condition=models.Q(master_medicine__isnull=False),
                violation_error_message="This pharmacy already lists this master medicine.",
            ),
        ]
        indexes = [
            models.Index(fields=["pharmacy", "is_available"]),
            models.Index(fields=["master_medicine", "is_available"]),
            # Partial index for enforced-null master_medicine entries
            models.Index(
                fields=["pharmacy"],
                condition=models.Q(master_medicine__isnull=True),
                name="idx_unlisted_listings",
            ),
        ]

    def __str__(self):
        name = (
            self.fallback_brand_name
            or (self.master_medicine.brand_name if self.master_medicine else "Unlisted")
        )
        return f"{self.pharmacy.name} — {name}"
