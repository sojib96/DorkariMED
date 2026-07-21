from django.contrib import admin

from .models import Pharmacy


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "phone", "is_active", "is_verified", "created_at")
    list_filter = ("is_active", "is_verified")
    search_fields = ("name", "owner__phone", "address")
    prepopulated_fields = {"slug": ("name",)}
