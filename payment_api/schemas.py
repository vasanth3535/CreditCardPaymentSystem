from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    card_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    simulate_failure: bool = False


class PaymentResponse(BaseModel):
    transaction_id: int
    transaction_reference: str
    card_id: int
    amount: Decimal
    status: str
