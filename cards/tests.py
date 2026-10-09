from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Card


class CardAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cardowner",
            password="StrongTestPass123!",
        )
        self.other_user = User.objects.create_user(
            username="otherowner",
            password="StrongTestPass123!",
        )
        self.card = Card.objects.create(
            user=self.other_user,
            card_holder_name="Other Owner",
            card_type="CREDIT",
            masked_card_number="**** **** **** 1234",
            last_four_digits="1234",
            expiry_date="12/28",
        )

    def test_card_list_requires_login(self):
        response = self.client.get(reverse("card_list"))
        self.assertEqual(response.status_code, 302)

    def test_users_only_see_their_own_cards(self):
        self.client.login(username="cardowner", password="StrongTestPass123!")
        response = self.client.get(reverse("card_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Other Owner")

    def test_add_card_stores_only_masked_number(self):
        self.client.login(username="cardowner", password="StrongTestPass123!")
        response = self.client.post(
            reverse("add_card"),
            {
                "card_holder_name": "Test Owner",
                "card_type": "CREDIT",
                "card_number": "4111111111115678",
                "expiry_date": "12/28",
            },
        )
        self.assertRedirects(response, reverse("card_list"))
        card = Card.objects.get(user=self.user)
        self.assertEqual(card.last_four_digits, "5678")
        self.assertEqual(card.masked_card_number, "**** **** **** 5678")
        self.assertNotIn("4111111111115678", card.masked_card_number)
