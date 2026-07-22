from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from pharmacies.models import Pharmacy


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    """Admin config for Pharmacy model."""

    list_display = (
        "name", "owner", "city", "division",
        "status", "is_verified", "phone", "created_at",
    )
    list_filter = ("status", "is_verified", "city", "division")
    search_fields = ("name", "owner__phone", "owner__full_name", "address_line", "city")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("owner", "name", "phone")}),
        (_("Address"), {"fields": ("address_line", "city", "division", "location")}),
        (_("Licensing"), {
            "fields": ("dgda_license_number", "pharmacist_name",
                       "pharmacist_registration_number"),
        }),
        (_("Operations"), {"fields": ("operating_hours", "status", "is_verified")}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
