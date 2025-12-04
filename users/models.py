"""
This file contains models for:
- UserProfile: stores phone number for each user
- OTP: stores OTP codes for login verification
"""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserProfile(models.Model):
    """
    Stores extra details for a user.
    In this project, it holds the user's phone number.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

    def __str__(self):
        """Return a simple readable display of the user and phone number."""
        return f"{self.user.username} - {self.phone_number}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a new User is created.
    Ensures every user has a matching profile.
    """
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={"phone_number": None}
        )


class OTP(models.Model):
    """
    Stores OTP codes for mobile number verification.
    Each OTP is valid for 5 minutes.
    """

    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        """
        Check if the OTP has expired.
        Returns True if more than 5 minutes old.
        """
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        """Return the phone number and OTP value."""
        return f"{self.phone_number} - {self.code}"
