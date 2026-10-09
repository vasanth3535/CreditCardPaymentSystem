from django.db import models
from django.contrib.auth.models import User


class Card(models.Model):
    CARD_TYPE_CHOICES = [
        ('CREDIT', 'Credit Card'),
        ('DEBIT', 'Debit Card'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cards'
    )
    card_holder_name = models.CharField(max_length=255)
    card_type = models.CharField(
        max_length=10,
        choices=CARD_TYPE_CHOICES,
        default='CREDIT'
    )
    masked_card_number = models.CharField(max_length=19)
    last_four_digits = models.CharField(max_length=4)
    expiry_date = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.card_holder_name} - {self.masked_card_number}"
