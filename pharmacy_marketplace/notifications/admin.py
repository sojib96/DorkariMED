from django.contrib import admin

from .models import NotifySubscription


@admin.register(NotifySubscription)
class NotifySubscriptionAdmin(admin.ModelAdmin):
    list_display = ("customer_phone", "master_medicine", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("customer_phone", "master_medicine__generic_name")
