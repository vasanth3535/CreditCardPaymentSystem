from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'transaction_reference',
            'card',
            'amount',
            'status',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'transaction_reference',
            'status',
            'created_at',
        ]
