from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "transaction_type",
        "amount",
        "timestamp",
        "sender",
        "receiver",
    )
    list_filter = ("transaction_type",)
    search_fields = ("sender__username", "receiver__username")
