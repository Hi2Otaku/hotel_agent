"""Pydantic v2 schemas for payment request/response contracts."""

from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentSubmit(BaseModel):
    """Step 3: Submit payment details to confirm booking."""

    card_number: str = Field(min_length=13, max_length=19)
    expiry_month: int = Field(ge=1, le=12)
    expiry_year: int
    cvc: str = Field(min_length=3, max_length=4)
    cardholder_name: str
    billing_address: str | None = None


class PaymentResponse(BaseModel):
    """Payment transaction result."""

    transaction_id: str
    status: str
    amount: Decimal
    currency: str
    card_last_four: str
    card_brand: str
    decline_reason: str | None = None

    model_config = {"from_attributes": True}
