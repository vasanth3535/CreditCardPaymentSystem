from decimal import Decimal, InvalidOperation

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rest_framework_simplejwt.tokens import RefreshToken

from cards.models import Card


FASTAPI_PAYMENT_URL = "http://127.0.0.1:8001/payments"


@login_required
def make_payment(request):
    user_cards = Card.objects.filter(user=request.user)

    if request.method == "POST":
        card_id = request.POST.get("card_id")
        amount = request.POST.get("amount")
        simulate_failure = request.POST.get("simulate_failure") == "true"

        if not card_id or not amount:
            messages.error(
                request,
                "Please select a card and enter a payment amount.",
            )
            return render(
                request,
                "transactions/payment.html",
                {"cards": user_cards},
            )

        try:
            amount_value = Decimal(amount)
        except (InvalidOperation, TypeError):
            messages.error(request, "Please enter a valid payment amount.")
            return render(
                request,
                "transactions/payment.html",
                {"cards": user_cards},
            )

        if not amount_value.is_finite() or amount_value <= 0:
            messages.error(
                request,
                "Payment amount must be a valid positive number.",
            )
            return render(
                request,
                "transactions/payment.html",
                {"cards": user_cards},
            )

        card = Card.objects.filter(
            id=card_id,
            user=request.user,
        ).first()

        if not card:
            messages.error(request, "Invalid card selected.")
            return render(
                request,
                "transactions/payment.html",
                {"cards": user_cards},
            )

        access_token = str(RefreshToken.for_user(request.user).access_token)

        try:
            response = requests.post(
                FASTAPI_PAYMENT_URL,
                json={
                    "card_id": card.id,
                    "amount": str(amount_value),
                    "simulate_failure": simulate_failure,
                },
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )

            if response.status_code == 201:
                result = response.json()

                if result["status"] == "SUCCESS":
                    messages.success(
                        request,
                        f"Payment successful. Reference: "
                        f"{result['transaction_reference']}",
                    )
                else:
                    messages.error(
                        request,
                        f"Payment failed. Reference: "
                        f"{result['transaction_reference']}",
                    )

                return redirect("transaction_history")

            try:
                error_data = response.json()
                error_message = error_data.get(
                    "detail",
                    "Payment processing failed.",
                )
            except ValueError:
                error_message = "Payment processing failed."

            messages.error(request, error_message)

        except requests.RequestException:
            messages.error(
                request,
                "Payment service is currently unavailable.",
            )

    return render(
        request,
        "transactions/payment.html",
        {"cards": user_cards},
    )
