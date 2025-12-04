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
    permission_classes = [permissions.IsAuthenticated]

    # GET endpoint — no request body
    def get(self, request):
        wallet = get_object_or_404(Wallet, user=request.user)
        serializer = WalletSerializer(wallet)
        # ensure Decimal is JSON serializable (as string)
        data = serializer.data
        data["balance"] = str(wallet.balance)
        return Response(data)


class WalletCreditView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=CreditSerializer, responses={200: WalletSerializer}
    )
    def post(self, request):
        serializer = CreditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data["amount"]
        remarks = serializer.validated_data.get("remarks", "")

        if amount <= 0:
            return Response(
                {"detail": "Amount must be positive"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
            {"balance": str(wallet.balance), "transaction_id": tx.id}, status=200
        )


class WalletDebitView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=DebitSerializer, responses={200: WalletSerializer}
    )
    def post(self, request):
        serializer = DebitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data["amount"]
        remarks = serializer.validated_data.get("remarks", "")

        if amount <= 0:
            return Response(
                {"detail": "Amount must be positive"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=request.user)
            if wallet.balance < amount:
                return Response(
                    {"detail": "Insufficient funds"},
                    status=status.HTTP_400_BAD_REQUEST,
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
            {"balance": str(wallet.balance), "transaction_id": tx.id}, status=200
        )


class WalletTransferView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=TransferSerializer)
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        to_phone = serializer.validated_data["to_phone_number"]
        amount = serializer.validated_data["amount"]
        remarks = serializer.validated_data.get("remarks", "")

        if amount <= 0:
            return Response(
                {"detail": "Amount must be positive"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # find receiver user
        try:
            receiver_user = User.objects.get(userprofile__phone_number=to_phone)
        except User.DoesNotExist:
            return Response(
                {"detail": "Receiver not found"}, status=status.HTTP_404_NOT_FOUND
            )

        with db_transaction.atomic():
            # lock both wallets (order by user id to avoid deadlocks)
            user_ids = sorted([request.user.id, receiver_user.id])
            wallets = (
                Wallet.objects.select_for_update()
                .filter(user_id__in=user_ids)
                .select_related("user")
            )

            # map user_id -> wallet
            wallet_map = {w.user_id: w for w in wallets}
            sender_wallet = wallet_map.get(request.user.id)
            receiver_wallet = wallet_map.get(receiver_user.id)

            if sender_wallet is None or receiver_wallet is None:
                return Response(
                    {"detail": "Sender or receiver wallet not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if sender_wallet.balance < amount:
                return Response(
                    {"detail": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST
                )

            sender_wallet.balance -= amount
            receiver_wallet.balance += amount

            sender_wallet.save()
            receiver_wallet.save()

            # create transaction records for both sides
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
    permission_classes = [permissions.IsAdminUser]
    queryset = Wallet.objects.select_related("user").all()
    serializer_class = WalletSerializer
