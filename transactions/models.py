"""
This model stores all wallet transactions.
Each entry represents one action such as:
- credit (add money)
- debit (remove money)
- transfer (send money to another user)
"""

from decimal import Decimal

from django.conf import settings
from django.db import models


class Transaction(models.Model):
    """
    Represents a single transaction in the system.
    This can be a CREDIT, DEBIT, or TRANSFER.
    """

    TRANSACTION_TYPES = (
        ("CREDIT", "Credit"),     # Money added to wallet
        ("DEBIT", "Debit"),       # Money taken from wallet
        ("TRANSFER", "Transfer"), # Money moved between users
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="sent_transactions",
        null=True,
        blank=True,
        help_text="User who sent the money (can be null for credit).",
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="received_transactions",
        null=True,
        blank=True,
        help_text="User who received the money (can be null for debit).",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Transaction amount.",
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        help_text="Type of transaction: CREDIT, DEBIT, or TRANSFER.",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the transaction occurred.",
    )

    remarks = models.TextField(
        blank=True,
        help_text="Optional notes or description about the transaction.",
    )

    def __str__(self):
        """
        Return a simple readable string for admin and logs.
        Example: 'CREDIT 100.00 2024-01-01 10:00:00'
        """
        return f"{self.transaction_type} {self.amount} {self.timestamp}"
