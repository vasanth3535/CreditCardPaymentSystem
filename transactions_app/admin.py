from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'transaction_reference',
        'user',
        'card',
        'amount',
        'status',
        'created_at',
    )
    search_fields = (
        'transaction_reference',
        'user__username',
        'card__last_four_digits',
    )
    list_filter = (
        'status',
        'created_at',
    )
    ordering = ('-created_at',)