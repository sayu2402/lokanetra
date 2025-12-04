from django.urls import path

from .views import TransactionListAdminView

urlpatterns = [
    path("admin-list/", TransactionListAdminView.as_view(), name="admin-transactions"),
]
