"""
Serializer for converting Transaction model data into JSON format.
Used for showing transaction details to admin or users.
"""

from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """
    Simple serializer for transaction records.
    Converts sender and receiver into readable strings.
    """
    sender = serializers.StringRelatedField()
    receiver = serializers.StringRelatedField()

    class Meta:
        model = Transaction
        fields = (
            "id",
            "sender",
            "receiver",
            "amount",
            "transaction_type",
            "timestamp",
            "remarks",
        )
