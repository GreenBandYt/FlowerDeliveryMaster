from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Phone Number"
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Address"
    )
    telegram_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Telegram ID"
    )

    def __str__(self):
        return self.username
