from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("seller", "Seller"),
        ("admin", "Admin"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="customer"
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True
    )

    email_verified = models.BooleanField(
        default=False
    )

    phone_verified = models.BooleanField(
        default=False
    )

    business_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    business_category = models.ForeignKey(
        'category.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.email or self.username

class SellerApplication(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="seller_application",
    )

    business_name = models.CharField(max_length=255)

    business_category = models.ForeignKey(
        "category.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.email} - {self.status}"


class SellerPayoutProfile(models.Model):
    seller = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="payout_profile",
    )

    account_holder_name = models.CharField(max_length=150)
    bank_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=34)
    ifsc_code = models.CharField(max_length=11)
    upi_id = models.CharField(max_length=120, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def masked_account_number(self):
        if len(self.account_number) <= 4:
            return self.account_number
        return f"{'*' * (len(self.account_number) - 4)}{self.account_number[-4:]}"

    def __str__(self):
        return f"Payout profile for {self.seller.username}"


class SellerPayoutRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("in_transit", "In Transit"),
        ("paid", "Paid"),
        ("rejected", "Rejected"),
        ("failed", "Failed"),
    )

    seller = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="payout_requests",
    )

    payout_profile = models.ForeignKey(
        SellerPayoutProfile,
        on_delete=models.PROTECT,
        related_name="payout_requests",
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    payout_reference = models.CharField(max_length=120, blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.seller.username} - ₹{self.amount} ({self.status})"