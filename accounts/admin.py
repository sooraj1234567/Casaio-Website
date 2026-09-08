from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


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