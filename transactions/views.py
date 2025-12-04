"""
This file contains the admin view for listing all transactions.
Admin can filter results using:
- date range
- transaction type
- sender phone
- receiver phone
- amount range
- search and ordering
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation

from rest_framework import filters, generics, permissions

from transactions.models import Transaction
from transactions.serializers import TransactionSerializer


class TransactionListAdminView(generics.ListAPIView):
    """
    Admin-only API to view all transactions.
    Supports filters such as:
    - start_date, end_date
    - transaction type
    - sender/receiver phone number
    - min_amount, max_amount
    Also supports search and ordering.
    """

    permission_classes = [permissions.IsAdminUser]
    serializer_class = TransactionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    # Search by username, transaction type, remarks
    search_fields = [
        "sender__username",
        "receiver__username",
        "transaction_type",
        "remarks",
    ]

    # Allow ordering by timestamp or amount
    ordering_fields = ["timestamp", "amount"]

    def _parse_date(self, value):
        """
        Convert a string (YYYY-MM-DD) into a date object.
        Returns None if the format is wrong.
        """
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    def _parse_decimal(self, value):
        """
        Convert a string/number into Decimal safely.
        Returns None if invalid.
        """
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None

    def get_queryset(self):
        """
        Apply all filters and return the transaction list.
        If any unexpected error happens, return an empty list.
        """
        try:
            qs = Transaction.objects.all()

            # --- DATE RANGE FILTER ---
            start_date = self._parse_date(self.request.query_params.get("start_date"))
            end_date = self._parse_date(self.request.query_params.get("end_date"))

            if start_date:
                qs = qs.filter(timestamp__date__gte=start_date)
            if end_date:
                qs = qs.filter(timestamp__date__lte=end_date)

            # --- TRANSACTION TYPE FILTER ---
            tx_type = self.request.query_params.get("type")
            if tx_type:
                qs = qs.filter(transaction_type=tx_type.strip().upper())

            # --- SENDER PHONE FILTER ---
            sender_phone = self.request.query_params.get("sender_phone")
            if sender_phone:
                qs = qs.filter(sender__userprofile__phone_number=sender_phone.strip())

            # --- RECEIVER PHONE FILTER ---
            receiver_phone = self.request.query_params.get("receiver_phone")
            if receiver_phone:
                qs = qs.filter(
                    receiver__userprofile__phone_number=receiver_phone.strip()
                )

            # --- AMOUNT RANGE FILTER ---
            min_amount = self._parse_decimal(
                self.request.query_params.get("min_amount")
            )
            max_amount = self._parse_decimal(
                self.request.query_params.get("max_amount")
            )

            if min_amount is not None:
                qs = qs.filter(amount__gte=min_amount)
            if max_amount is not None:
                qs = qs.filter(amount__lte=max_amount)

            # Return newest transactions first
            return qs.order_by("-timestamp")

        except Exception:
            # Do not break the API — return empty results if something goes wrong
            return Transaction.objects.none()
