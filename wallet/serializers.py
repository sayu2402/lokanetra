"""
This file contains serializers for wallet operations:
- viewing wallet balance
- crediting money
- debiting money
- transferring money to another user
"""

from rest_framework import serializers

from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer to show wallet details such as user and balance.
    """

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Wallet
        fields = ("user", "balance")


class CreditSerializer(serializers.Serializer):
    """
    Serializer for adding money to a wallet.
    Requires an amount and optional remarks.
    """

    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    remarks = serializers.CharField(required=False, allow_blank=True)


class DebitSerializer(serializers.Serializer):
    """
    Serializer for removing money from a wallet.
    Only the amount is required.
    """

    amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class TransferSerializer(serializers.Serializer):
    """
    Serializer for transferring money to another user.
    Requires receiver phone number, amount, and optional remarks.
    """

    to_phone_number = serializers.CharField(max_length=15)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    remarks = serializers.CharField(required=False, allow_blank=True)
