"""Mock payment processing with test card outcomes.

Simulates a payment gateway with configurable test cards for
development and integration testing.
"""

import asyncio
import uuid
from decimal import Decimal

# Test cards with deterministic outcomes for development
TEST_CARDS: dict[str, dict] = {
    "4242424242424242": {"status": "succeeded", "brand": "visa"},
    "4000000000000002": {
        "status": "declined",
        "brand": "visa",
        "reason": "card_declined",
    },
    "4111111111111111": {
        "status": "declined",
        "brand": "visa",
        "reason": "insufficient_funds",
    },
}


async def process_payment(
    card_number: str, amount: Decimal, currency: str = "USD"
) -> dict:
    """Process a mock payment and return the transaction result.

    Simulates real-world processing delay (2.5 seconds).
    Uses TEST_CARDS for deterministic outcomes; unknown cards default to success.

    Args:
        card_number: The card number to charge.
        amount: The charge amount (Decimal).
        currency: ISO 4217 currency code (default USD).

    Returns:
        Dict with transaction_id, status, brand, last_four, amount, currency,
        and optional decline_reason.
    """
    # Simulate payment gateway processing time
    await asyncio.sleep(2.5)

    card_info = TEST_CARDS.get(
        card_number, {"status": "succeeded", "brand": "visa"}
    )

    transaction_id = f"txn_{uuid.uuid4().hex[:16]}"

    return {
        "transaction_id": transaction_id,
        "status": card_info["status"],
        "brand": card_info["brand"],
        "last_four": card_number[-4:],
        "amount": amount,
        "currency": currency,
        "decline_reason": card_info.get("reason"),
    }
