import os
from unittest.mock import MagicMock

import jwt
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from payment_api.database import get_db
from payment_api.main import app

load_dotenv()
JWT_SECRET_KEY = os.getenv("SECRET_KEY", "default-key")


def create_access_token(user_id=1):
    return jwt.encode(
        {
            "user_id": user_id,
            "token_type": "access",
        },
        JWT_SECRET_KEY,
        algorithm="HS256",
    )


def create_mock_db(card_exists=True, card_user_id=1):
    db = MagicMock()
    card_result = MagicMock()

    if card_exists:
        card_result.mappings.return_value.first.return_value = {
            "id": 1,
            "user_id": card_user_id,
        }
    else:
        card_result.mappings.return_value.first.return_value = None

    db.execute.return_value = card_result

    def add_transaction(transaction):
        transaction.id = 1

    db.add.side_effect = add_transaction
    return db


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def payment_headers(user_id=1):
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


def test_successful_payment(client):
    mock_db = create_mock_db()
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/payments",
        headers=payment_headers(),
        json={
            "card_id": 1,
            "amount": 500.00,
            "simulate_failure": False,
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "SUCCESS"


def test_failed_payment(client):
    mock_db = create_mock_db()
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/payments",
        headers=payment_headers(),
        json={
            "card_id": 1,
            "amount": 500.00,
            "simulate_failure": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "FAILED"


def test_invalid_card(client):
    mock_db = create_mock_db(card_exists=False)
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/payments",
        headers=payment_headers(),
        json={
            "card_id": 999,
            "amount": 500.00,
            "simulate_failure": False,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Card not found"


def test_missing_token(client):
    response = client.post(
        "/payments",
        json={
            "card_id": 1,
            "amount": 500.00,
            "simulate_failure": False,
        },
    )

    assert response.status_code == 401


def test_invalid_token(client):
    response = client.post(
        "/payments",
        headers={"Authorization": "Bearer invalid-token"},
        json={
            "card_id": 1,
            "amount": 500.00,
            "simulate_failure": False,
        },
    )

    assert response.status_code == 401


def test_cannot_pay_with_another_users_card(client):
    mock_db = create_mock_db(card_user_id=2)
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/payments",
        headers=payment_headers(user_id=1),
        json={
            "card_id": 1,
            "amount": 500.00,
            "simulate_failure": False,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You are not authorized to use this card"
    )
