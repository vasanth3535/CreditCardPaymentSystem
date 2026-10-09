import os
from uuid import uuid4

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from payment_api.database import get_db
from payment_api.models import Transaction
from payment_api.schemas import PaymentCreate, PaymentResponse

load_dotenv()

JWT_SECRET_KEY = os.getenv("SECRET_KEY", "default-key")
bearer_scheme = HTTPBearer(auto_error=False)

app = FastAPI(
    title="Credit Card Payment API",
    description="JWT-protected payment processing API",
    version="1.0.0",
)


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=["HS256"],
        )
        user_id = payload.get("user_id")

        if payload.get("token_type") != "access" or user_id is None:
            raise jwt.InvalidTokenError("Invalid access token")

        return int(user_id)

    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/")
def root():
    return {"message": "Credit Card Payment API is running"}


@app.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def make_payment(
    payment: PaymentCreate,
    user_id: int = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    card = db.execute(
        text("""
            SELECT id, user_id
            FROM cards_card
            WHERE id = :card_id
        """),
        {"card_id": payment.card_id},
    ).mappings().first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )

    if int(card["user_id"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to use this card",
        )

    transaction_reference = f"TXN-{uuid4().hex[:12].upper()}"

    transaction = Transaction(
        user_id=user_id,
        card_id=payment.card_id,
        amount=payment.amount,
        status="PENDING",
        transaction_reference=transaction_reference,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    transaction.status = (
        "FAILED" if payment.simulate_failure else "SUCCESS"
    )

    db.commit()
    db.refresh(transaction)

    return PaymentResponse(
        transaction_id=transaction.id,
        transaction_reference=transaction.transaction_reference,
        card_id=transaction.card_id,
        amount=transaction.amount,
        status=transaction.status,
    )
