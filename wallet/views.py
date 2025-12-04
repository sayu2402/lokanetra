"""
This file contains all wallet-related API views.
It includes:
- Get wallet balance
- Add money (credit)
- Reduce money (debit)
- Transfer money to another user
- Admin: list all wallets
"""

from django.contrib.auth.models import User
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from transactions.models import Transaction
from .models import Wallet
from .serializers import (
    CreditSerializer,
    DebitSerializer,
    TransferSerializer,
    WalletSerializer,
)


class WalletBalanceView(views.APIView):
    """
    Get the logged-in user's wallet balance.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Return the current balance of the user's wallet.
        """
        wallet = get_object_or_404(Wallet, user=request.user)
        serializer = WalletSerializer(wallet)

        data = serializer.data
        data["balance"] = str(wallet.balance)  # Convert Decimal to string

        return Response(data)


class WalletCreditView(views.APIView):
    """
    Add money to the user's wallet (credit).
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=CreditSerializer,
        responses={200: WalletSerializer}
    )
    def post(self, request):
        """
        Increase wallet balance by the given amount.
        """
        serializer = CreditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        remarks = serializer.validated_data.get("remarks", "")

        if amount <= 0:
            return Response(
                {"detail": "Amount must be positive"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Perform safe update
        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=request.user)
            wallet.balance += amount
            wallet.save()

            tx = Transaction.objects.create(
                sender=None,
                receiver=request.user,
                amount=amount,
                transaction_type="CREDIT",
                remarks=remarks,
            )

        return Response(
            {"balance": str(wallet.balance), "transaction_id": tx.id}
        )


class WalletDebitView(views.APIView):
    """
    Reduce money from the user's wallet (debit).
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=DebitSerializer,
        responses={200: WalletSerializer}
    )
    def post(self, request):
        """
        Decrease wallet balance if user has enough money.
        """
        serializer = DebitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        remarks = serializer.validated_data.get("remarks", "")

        if amount <= 0:
            return Response(
                {"detail": "Amount must be positive"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=request.user)

            if wallet.balance < amount:
                return Response(
                    {"detail": "Insufficient funds"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            wallet.balance -= amount
            wallet.save()

            tx = Transaction.objects.create(
                sender=request.user,
                receiver=None,
                amount=amount,
                transaction_type="DEBIT",
                remarks=remarks,
            )

        return Response(
            {"balance": str(wallet.balance), "transaction_id": tx.id}
        )


class WalletTransferView(views.APIView):
    """
    Transfer money from the logged-in user to another user.
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=TransferSerializer)
    def post(self, request):
        """
        Move money from sender to receiver using phone number.
        """
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        to_phone = serializer.validated_data["to_phone_number"]
        amount = serializer.validated_data["amount"]
        remarks = serializer.validated_data.get("remarks", "")

        if amount <= 0:
            return Response(
                {"detail": "Amount must be positive"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find receiver
        try:
            receiver_user = User.objects.get(userprofile__phone_number=to_phone)
        except User.DoesNotExist:
            return Response(
                {"detail": "Receiver not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        with db_transaction.atomic():
            # Lock wallets safely
            ids = sorted([request.user.id, receiver_user.id])
            wallets = Wallet.objects.select_for_update().filter(user_id__in=ids)

            wallet_map = {wallet.user_id: wallet for wallet in wallets}
            sender_wallet = wallet_map.get(request.user.id)
            receiver_wallet = wallet_map.get(receiver_user.id)

            if sender_wallet.balance < amount:
                return Response(
                    {"detail": "Insufficient funds"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update balances
            sender_wallet.balance -= amount
            receiver_wallet.balance += amount
            sender_wallet.save()
            receiver_wallet.save()

            # Log transaction entries
            debit_tx = Transaction.objects.create(
                sender=request.user,
                receiver=receiver_user,
                amount=amount,
                transaction_type="DEBIT",
                remarks=remarks,
            )
            credit_tx = Transaction.objects.create(
                sender=request.user,
                receiver=receiver_user,
                amount=amount,
                transaction_type="CREDIT",
                remarks=remarks,
            )

        return Response(
            {
                "message": "Transfer successful",
                "debit_transaction_id": debit_tx.id,
                "credit_transaction_id": credit_tx.id,
                "sender_balance": str(sender_wallet.balance),
                "receiver_balance": str(receiver_wallet.balance),
            }
        )


class WalletListAdminView(generics.ListAPIView):
    """
    Admin-only view that returns all wallets with user info.
    """

    permission_classes = [permissions.IsAdminUser]
    queryset = Wallet.objects.select_related("user").all()
    serializer_class = WalletSerializer
