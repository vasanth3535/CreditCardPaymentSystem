from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from cards.models import Card
from .models import Transaction


class TransactionAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="txnowner",
            password="StrongTestPass123!",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="StrongTestPass123!",
        )
        self.card = Card.objects.create(
            user=self.user,
            card_holder_name="Transaction Owner",
            card_type="CREDIT",
            masked_card_number="**** **** **** 5678",
            last_four_digits="5678",
            expiry_date="12/28",
        )
        self.transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("125.00"),
            status="SUCCESS",
            transaction_reference="TXN-TEST-0001",
        )
        self.client = APIClient()

    def test_transaction_list_requires_authentication(self):
        response = self.client.get(reverse("transaction_list"))
        self.assertIn(response.status_code, (401, 403))

    def test_authenticated_user_sees_own_transactions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("transaction_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["transaction_reference"],
            "TXN-TEST-0001",
        )

    def test_user_cannot_retrieve_another_users_transaction(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(
            reverse("transaction_detail", args=[self.transaction.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_transaction_history_requires_login(self):
        response = self.client.get(reverse("transaction_history"))
        self.assertEqual(response.status_code, 302)
