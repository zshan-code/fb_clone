# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    is_email_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True, default="")

    REQUIRED_FIELDS = ["email"]
    USERNAME_FIELD = "username"

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"
