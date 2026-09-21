from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, SellerPayoutProfile, SellerPayoutRequest


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "role",
        "phone_number",
        "email_verified",
        "phone_verified",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "email_verified",
        "phone_verified",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "phone_number",
    )

    ordering = ("-date_joined",)

    # Extend UserAdmin fieldsets to display custom fields
    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "email_verified",
                    "phone_verified",
                )
            },
        ),
    )

    # Extend add_fieldsets for creating users from admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "role",
                    "phone_number",
                )
            },
        ),
    )


@admin.register(SellerPayoutProfile)
class SellerPayoutProfileAdmin(admin.ModelAdmin):
    list_display = (
        "seller",
        "bank_name",
        "masked_account_number",
        "ifsc_code",
        "is_verified",
        "updated_at",
    )
    list_filter = ("is_verified", "bank_name")
    search_fields = ("seller__username", "seller__email", "account_holder_name", "ifsc_code")
    readonly_fields = ("masked_account_number", "created_at", "updated_at")


@admin.register(SellerPayoutRequest)
class SellerPayoutRequestAdmin(admin.ModelAdmin):
    list_display = (
        "seller",
        "amount",
        "status",
        "payout_reference",
        "requested_at",
    )
    list_filter = ("status", "requested_at")
    search_fields = ("seller__username", "seller__email", "payout_reference")
    readonly_fields = ("requested_at", "processed_at")