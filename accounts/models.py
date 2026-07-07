from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)


    def __str__(self):
        return self.email