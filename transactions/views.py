from datetime import datetime
from decimal import Decimal, InvalidOperation

from rest_framework import filters, generics, permissions

from transactions.models import Transaction
from transactions.serializers import TransactionSerializer


class TransactionListAdminView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = TransactionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "sender__username",
        "receiver__username",
        "transaction_type",
        "remarks",
    ]
    ordering_fields = ["timestamp", "amount"]

    def _parse_date(self, value):
        # Expecting YYYY-MM-DD. Return datetime.date or None if invalid.
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    def _parse_decimal(self, value):
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None

    def get_queryset(self):
        try:
            qs = Transaction.objects.all()
            # DATE RANGE
            start_date = self._parse_date(self.request.query_params.get("start_date"))
            end_date = self._parse_date(self.request.query_params.get("end_date"))
            if start_date:
                qs = qs.filter(timestamp__date__gte=start_date)
            if end_date:
                qs = qs.filter(timestamp__date__lte=end_date)

            # TRANSACTION TYPE
            tx_type = self.request.query_params.get("type")
            if tx_type:
                qs = qs.filter(transaction_type=tx_type.strip().upper())

            # SENDER PHONE
            sender_phone = self.request.query_params.get("sender_phone")
            if sender_phone:
                # if sender is null this will simply not match
                qs = qs.filter(sender__userprofile__phone_number=sender_phone.strip())

            # RECEIVER PHONE
            receiver_phone = self.request.query_params.get("receiver_phone")
            if receiver_phone:
                qs = qs.filter(
                    receiver__userprofile__phone_number=receiver_phone.strip()
                )

            # AMOUNT RANGE
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

            return qs.order_by("-timestamp")
        except Exception:
            # NEVER return None — return an empty queryset on unexpected errors
            return Transaction.objects.none()
