"""Regression tests for FIX-003.

Incident: Inventory anomaly — negative reservation inflated stock.
Root cause (RCA-003): reserve_stock() subtracted the caller-supplied qty from
    STOCK with no validation. A negative qty (e.g. -5) caused
    STOCK[item] -= -5, which *increased* the stock level.
Fix: a guard at the top of reserve_stock() raises ValueError for any qty
    that is zero or negative before any mutation of STOCK occurs.

These tests FAIL on the pre-fix code (no guard) and
PASS on the fixed code (ValueError guard).
"""

import pytest

from app import inventory
from app.main import create_app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_stock():
    """Restore inventory to baseline so tests are order-independent."""
    inventory.STOCK.clear()
    inventory.STOCK.update({"widget": 100, "gadget": 50})
    yield
    inventory.STOCK.clear()
    inventory.STOCK.update({"widget": 100, "gadget": 50})


@pytest.fixture()
def client():
    """Flask test client."""
    app = create_app()
    app.testing = True
    return app.test_client()


# ---------------------------------------------------------------------------
# Exact incident scenario — negative qty raises ValueError and does not mutate
# ---------------------------------------------------------------------------


def test_reserve_stock_negative_qty_raises_value_error():
    """reserve_stock() with qty=-5 must raise ValueError.

    Pre-fix: STOCK['widget'] -= -5 → stock increases to 105  (BUG)
    Post-fix: ValueError("qty must be positive, got -5") is raised immediately.
    """
    with pytest.raises(ValueError, match="qty must be positive"):
        inventory.reserve_stock("widget", -5)


def test_reserve_stock_negative_qty_does_not_mutate_stock():
    """Stock must remain unchanged when a negative qty is rejected."""
    with pytest.raises(ValueError):
        inventory.reserve_stock("widget", -5)
    assert inventory.STOCK["widget"] == 100


# ---------------------------------------------------------------------------
# Edge cases around the fix
# ---------------------------------------------------------------------------


def test_reserve_stock_zero_qty_raises_value_error():
    """Zero qty is also invalid (no-op reservation) and must raise ValueError."""
    with pytest.raises(ValueError, match="qty must be positive"):
        inventory.reserve_stock("widget", 0)


def test_reserve_stock_zero_qty_does_not_mutate_stock():
    """Stock must remain unchanged when qty=0 is rejected."""
    with pytest.raises(ValueError):
        inventory.reserve_stock("widget", 0)
    assert inventory.STOCK["widget"] == 100


def test_reserve_stock_positive_qty_still_works():
    """Positive qty must still reduce stock correctly after the fix."""
    remaining = inventory.reserve_stock("widget", 10)
    assert remaining == 90
    assert inventory.STOCK["widget"] == 90


def test_reserve_endpoint_negative_qty_raises_and_leaves_stock_intact():
    """POST /reserve with a negative qty must not inflate stock.

    The /reserve endpoint has no try/except, so ValueError propagates as an
    unhandled exception. We verify only that stock is not mutated (the guard
    fires before STOCK is touched).
    """
    app = create_app()
    app.testing = False  # suppress exception propagation so we get a 500 response
    c = app.test_client()
    resp = c.post("/reserve", json={"item": "widget", "qty": -3})
    assert resp.status_code == 500
    assert inventory.STOCK["widget"] == 100  # stock untouched


def test_reserve_stock_error_message_contains_bad_qty():
    """The ValueError message must identify the rejected qty."""
    with pytest.raises(ValueError, match="-10"):
        inventory.reserve_stock("widget", -10)
