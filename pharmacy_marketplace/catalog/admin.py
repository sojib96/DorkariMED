from django.contrib import admin

from .models import MasterMedicine, PharmacyMedicineListing


@admin.register(MasterMedicine)
class MasterMedicineAdmin(admin.ModelAdmin):
    list_display = ("generic_name", "brand_name", "dosage_form", "strength", "manufacturer")
    search_fields = ("generic_name", "brand_name")
    list_filter = ("dosage_form",)


@admin.register(PharmacyMedicineListing)
class PharmacyMedicineListingAdmin(admin.ModelAdmin):
    list_display = (
        "pharmacy",
        "master_medicine",
        "price",
        "is_available",
        "created_at",
    )
    list_filter = ("is_available", "pharmacy")
    search_fields = ("pharmacy__name", "master_medicine__generic_name")
    # Phase 2 will add: bulk normalization actions
