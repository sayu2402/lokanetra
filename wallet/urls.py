"""
URL routes for wallet operations.
Includes:
- checking balance
- crediting money
- debiting money
- transferring money
- admin wallet list
"""

from django.urls import path

from .views import (
    WalletBalanceView,
    WalletCreditView,
    WalletDebitView,
    WalletListAdminView,
    WalletTransferView,
)

urlpatterns = [
    # Get the logged-in user's wallet balance
    path("balance/", WalletBalanceView.as_view(), name="wallet-balance"),

    # Add money to the wallet
    path("credit/", WalletCreditView.as_view(), name="wallet-credit"),

    # Remove money from the wallet
    path("debit/", WalletDebitView.as_view(), name="wallet-debit"),

    # Transfer money to another user
    path("transfer/", WalletTransferView.as_view(), name="wallet-transfer"),

    # Admin view to list all wallets
    path("admin/wallets/", WalletListAdminView.as_view(), name="admin-wallets"),
]
