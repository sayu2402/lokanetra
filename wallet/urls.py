from django.urls import path

from .views import (
    WalletBalanceView,
    WalletCreditView,
    WalletDebitView,
    WalletListAdminView,
    WalletTransferView,
)

urlpatterns = [
    path("balance/", WalletBalanceView.as_view(), name="wallet-balance"),
    path("credit/", WalletCreditView.as_view(), name="wallet-credit"),
    path("debit/", WalletDebitView.as_view(), name="wallet-debit"),
    path("transfer/", WalletTransferView.as_view(), name="wallet-transfer"),
    path("admin/wallets/", WalletListAdminView.as_view(), name="admin-wallets"),
]
