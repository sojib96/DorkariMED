from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from accounts.models import OTPCode, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin config for the custom User model with role-based access."""

    list_display = (
        "phone", "full_name", "role", "is_phone_verified",
        "is_active", "is_staff", "created_at",
    )
    list_filter = ("role", "is_active", "is_phone_verified", "is_staff")
    search_fields = ("phone", "full_name", "email")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        (_("Personal info"), {"fields": ("full_name", "email", "role")}),
        (
            _("Location"),
            {
                "fields": ("default_latitude", "default_longitude"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_phone_verified",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "full_name", "email", "role", "password1", "password2"),
            },
        ),
    )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    """Admin view for OTP codes (read-only, for debugging)."""

    list_display = ("phone", "is_verified", "attempts", "created_at", "expires_at")
    list_filter = ("is_verified",)
    search_fields = ("phone",)
    ordering = ("-created_at",)
    readonly_fields = ("phone", "code", "attempts", "is_verified", "created_at", "expires_at")
