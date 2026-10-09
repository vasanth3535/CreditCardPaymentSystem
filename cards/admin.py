from django.contrib import admin

from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'card_holder_name',
        'masked_card_number',
        'last_four_digits',
        'expiry_date',
        'created_at',
    )
    search_fields = (
        'card_holder_name',
        'last_four_digits',
    )
    list_filter = (
        'expiry_date',
        'created_at',
    )