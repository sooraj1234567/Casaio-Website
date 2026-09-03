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

    def __str__(self):
        return self.email