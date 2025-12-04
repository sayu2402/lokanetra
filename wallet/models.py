"""
Wallet model stores the balance for each user.
Every user has one wallet created during OTP verification.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models


class Wallet(models.Model):
    """
    Represents a user's wallet.
    Stores the total balance available for that user.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    def __str__(self):
        """Return a readable wallet display with username and balance."""
        return f"{self.user.username} wallet - {self.balance}"
