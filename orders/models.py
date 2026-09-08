from django.conf import settings
from django.db import models
from django.utils import timezone


class Order(models.Model):

    PAYMENT_CHOICES = (
        ("cod", "Cash on Delivery"),
        ("razorpay", "Razorpay"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    order_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    address = models.ForeignKey(
        "checkout.Address",
        on_delete=models.PROTECT
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES
    )

    payment_status = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    razorpay_order_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    razorpay_signature = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            super().save(*args, **kwargs)
            date = timezone.now().strftime("%Y%m%d")
            self.order_number = f"CAS-{date}-{self.id:06d}"
            super().save(update_fields=["order_number"])
            return

        super().save(*args, **kwargs)

    def update_status_from_items(self):
        """Automatically synchronizes the parent order status and payment status based on its item statuses."""
        if self.status == "cancelled":
            return

        items = self.items.all()
        if not items.exists():
            return

        # Normalize item statuses to lowercase to prevent case mismatch issues
        statuses = [str(item.status).lower().strip() for item in items]

        if all(s == "delivered" for s in statuses):
            self.status = "delivered"
            if self.payment_method == "cod":
                self.payment_status = True  # Mark paid upon delivery for COD
        elif any(s == "shipped" for s in statuses):
            self.status = "shipped"
        elif any(s == "confirmed" for s in statuses):
            self.status = "confirmed"
        elif all(s == "cancelled" for s in statuses):
            self.status = "cancelled"
            if self.payment_method == "cod":
                self.payment_status = False
        else:
            self.status = "pending"
        
        self.save(update_fields=["status", "payment_status"])

    def __str__(self):
        return self.order_number or f"Order #{self.id}"


class OrderItem(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        "product.Product",
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    @property
    def total_price(self):
        return self.selling_price * self.quantity

    def save(self, *args, **kwargs):
        """Automatically update parent order status whenever an order item is saved."""
        super().save(*args, **kwargs)
        if self.order:
            self.order.update_status_from_items()

    def __str__(self):
        return f"{self.product.name} - {self.status}"


class Coupon(models.Model):

    DISCOUNT_CHOICES = (
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    )

    code = models.CharField(
        max_length=50,
        unique=True
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_CHOICES,
        default="percentage"
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    minimum_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    maximum_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    used_count = models.PositiveIntegerField(
        default=0
    )

    valid_from = models.DateTimeField()

    valid_until = models.DateTimeField()

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.code