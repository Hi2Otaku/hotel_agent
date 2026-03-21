"""Unit tests for the mock payment processing service.

Tests all test card outcomes and default behavior.
"""

from decimal import Decimal

import pytest


@pytest.mark.asyncio
async def test_process_payment_success():
    """Card 4242424242424242 returns status succeeded."""
    from app.services.payment import process_payment

    result = await process_payment("4242424242424242", Decimal("100.00"))
    assert result["status"] == "succeeded"
    assert result["brand"] == "visa"
    assert result["last_four"] == "4242"
    assert result["amount"] == Decimal("100.00")
    assert result["currency"] == "USD"
    assert result["decline_reason"] is None


@pytest.mark.asyncio
async def test_process_payment_declined():
    """Card 4000000000000002 returns status declined with card_declined reason."""
    from app.services.payment import process_payment

    result = await process_payment("4000000000000002", Decimal("50.00"))
    assert result["status"] == "declined"
    assert result["decline_reason"] == "card_declined"
    assert result["last_four"] == "0002"


@pytest.mark.asyncio
async def test_process_payment_insufficient_funds():
    """Card 4111111111111111 returns insufficient_funds reason."""
    from app.services.payment import process_payment

    result = await process_payment("4111111111111111", Decimal("999.99"))
    assert result["status"] == "declined"
    assert result["decline_reason"] == "insufficient_funds"
    assert result["last_four"] == "1111"


@pytest.mark.asyncio
async def test_process_payment_unknown_card_succeeds():
    """Unknown card numbers default to success."""
    from app.services.payment import process_payment

    result = await process_payment("5555555555554444", Decimal("200.00"))
    assert result["status"] == "succeeded"
    assert result["brand"] == "visa"


@pytest.mark.asyncio
async def test_transaction_id_format():
    """Transaction ID starts with txn_ prefix."""
    from app.services.payment import process_payment

    result = await process_payment("4242424242424242", Decimal("10.00"))
    assert result["transaction_id"].startswith("txn_")
    assert len(result["transaction_id"]) == 20  # "txn_" + 16 hex chars
