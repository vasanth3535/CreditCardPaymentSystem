from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthenticationTests(TestCase):
    def test_registration_hashes_password(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "testuser",
                "email": "test@example.com",
                "password": "StrongTestPass123!",
            },
        )
        user = User.objects.get(username="testuser")
        self.assertNotEqual(user.password, "StrongTestPass123!")
        self.assertTrue(user.check_password("StrongTestPass123!"))
        self.assertRedirects(response, reverse("card_list"))

    def test_login_with_valid_credentials(self):
        User.objects.create_user(
            username="loginuser",
            password="StrongTestPass123!",
        )
        response = self.client.post(
            reverse("login"),
            {
                "username": "loginuser",
                "password": "StrongTestPass123!",
            },
        )
        self.assertRedirects(response, reverse("card_list"))

    def test_login_rejects_invalid_password(self):
        User.objects.create_user(
            username="loginuser",
            password="StrongTestPass123!",
        )
        response = self.client.post(
            reverse("login"),
            {"username": "loginuser", "password": "wrong-password"},
        )
        self.assertRedirects(response, reverse("login"))
