from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 2


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "image_preview",
        "name",
        "category",
        "selling_price",
        "stock",
        "is_available",
    )

    list_filter = (
        "category",
        "is_available",
    )

    search_fields = (
        "name",
        "category__name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    readonly_fields = (
        "image_preview",
    )

    ordering = ("name",)

    inlines = [ProductImageInline, ProductVariantInline,]

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:8px; object-fit:cover;">',
                obj.image.url,
            )
        return "No Image"

    image_preview.short_description = "Preview"