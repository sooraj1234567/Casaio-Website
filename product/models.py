from django.db import models
from django.utils.text import slugify
from category.models import Category


class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=200)

    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField()

    # Dropshipping Pricing
    supplier_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    is_offer_active = models.BooleanField(default=False)

    offer_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    discount_percentage = models.PositiveIntegerField(default=0)

    stock = models.PositiveIntegerField(default=0)

    image = models.ImageField(
        upload_to="products/"
    )

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        # Calculate discount
        if (
            self.is_offer_active
            and self.offer_price
            and self.offer_price < self.selling_price
        ):
            self.discount_percentage = int(
                (
                    (self.selling_price - self.offer_price)
                    / self.selling_price
                ) * 100
            )
        else:
            self.discount_percentage = 0
            self.offer_price = None

        super().save(*args, **kwargs)

    @property
    def current_price(self):
        if self.is_offer_active and self.offer_price:
            return self.offer_price
        return self.selling_price

    @property
    def profit(self):
        return self.current_price - self.supplier_price

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="products/gallery/")

    def __str__(self):
        return f"{self.product.name} Image"

class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    variant_name = models.CharField(max_length=100)
    variant_value = models.CharField(max_length=100)

    additional_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.variant_name}: {self.variant_value}"
