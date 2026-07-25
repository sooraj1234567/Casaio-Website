from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "phone_number",
        "email_verified",
        "phone_verified",
        "is_staff",
        "is_active",
    )

    list_filter = (
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