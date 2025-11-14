# apps/profiles/models.py
from django.db import models
from django.conf import settings
from datetime import date

class Profile(models.Model):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    GENDER_CHOICES = [(MALE,"Male"), (FEMALE,"Female"), (OTHER,"Other / Prefer not to say")]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    bio = models.TextField(blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def age(self):
        if not self.dob:
            return None
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def __str__(self):
        return f"Profile of {self.user.username}"
