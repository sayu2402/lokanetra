"""
URL routes for transaction-related admin operations.
Includes:
- admin list of all transactions
"""

from django.urls import path

from .views import TransactionListAdminView

urlpatterns = [
    # Admin endpoint to view all transactions with filters
    path("admin-list/", TransactionListAdminView.as_view(), name="admin-transactions"),
]
