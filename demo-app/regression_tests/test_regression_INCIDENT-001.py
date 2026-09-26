"""Regression tests for INCIDENT-001 (three separate bugs).

These tests pin the exact failing scenarios described in the incident
reports and must FAIL on the pre-fix code and PASS on the fixed code.

Covers:
  RCA-001 — currency.convert() raises KeyError for unsupported codes (EUR)
  RCA-002 — apply_discount() ignores lowercase discount codes silently
  RCA-003 — reserve_stock() accepts negative qty and inflates stock
"""

import pytest

from app import currency, discounts, inventory
from app.main import create_app


# ---------------------------------------------------------------------------
# Shared fixtures
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
# RCA-001: currency.convert() — unsupported currency raises ValueError (not KeyError)
# ---------------------------------------------------------------------------


def test_convert_eur_raises_value_error():
    """EUR is not in SUPPORTED_CURRENCIES; must raise ValueError, not KeyError."""
    with pytest.raises(ValueError, match="Unsupported currency"):
        currency.convert(100.0, "EUR")


def test_convert_unknown_code_raises_value_error():
    """Any arbitrary unsupported code must raise ValueError."""
    with pytest.raises(ValueError):
        currency.convert(50.0, "JPY")


def test_checkout_eur_returns_500_not_unhandled_key_error(client):
    """POST /checkout with EUR must return HTTP 500 with an error message
    (not crash with an unhandled KeyError traceback)."""
    resp = client.post(
        "/checkout",
        json={
            "items": [{"sku": "widget", "price": 100.0, "qty": 1}],
            "currency": "EUR",
        },
    )
    assert resp.status_code == 500
    body = resp.get_json()
    assert "error" in body
    # The error message should describe the unsupported currency, not be a raw key repr
    assert "EUR" in body["error"]


def test_convert_supported_currencies_still_work():
    """Supported currencies (USD, INR, GBP) must still convert correctly."""
    assert currency.convert(100.0, "USD") == pytest.approx(100.0)
    assert currency.convert(100.0, "INR") == pytest.approx(8320.0)
    assert currency.convert(100.0, "GBP") == pytest.approx(79.0)


# ---------------------------------------------------------------------------
# RCA-002: apply_discount() — case-insensitive lookup
# ---------------------------------------------------------------------------


def test_apply_discount_lowercase_save10():
    """Lowercase 'save10' must apply the 10 % discount (was silently ignored)."""
    result = discounts.apply_discount("save10", 100.0)
    assert result == pytest.approx(90.0)


def test_apply_discount_mixed_case_welcome20():
    """Mixed-case 'Welcome20' must apply the 20 % discount."""
    result = discounts.apply_discount("Welcome20", 200.0)
    assert result == pytest.approx(160.0)


def test_apply_discount_uppercase_still_works():
    """Exact-uppercase codes must still work after the fix."""
    assert discounts.apply_discount("SAVE10", 100.0) == pytest.approx(90.0)
    assert discounts.apply_discount("WELCOME20", 100.0) == pytest.approx(80.0)


def test_apply_discount_none_code_no_discount():
    """None code must still return the full subtotal."""
    assert discounts.apply_discount(None, 150.0) == pytest.approx(150.0)


def test_discount_endpoint_lowercase_code(client):
    """POST /discount with lowercase 'save10' must return 90.0 (was 100.0 before fix)."""
    resp = client.post("/discount", json={"code": "save10", "subtotal": 100})
    assert resp.status_code == 200
    assert resp.get_json()["discounted_total"] == pytest.approx(90.0)


# ---------------------------------------------------------------------------
# RCA-003: reserve_stock() — negative qty must be rejected
# ---------------------------------------------------------------------------


def test_reserve_stock_negative_qty_raises_value_error():
    """Negative qty must raise ValueError (was silently inflating stock)."""
    with pytest.raises(ValueError, match="qty must be positive"):
        inventory.reserve_stock("widget", -5)


def test_reserve_stock_negative_qty_does_not_mutate_stock():
    """Stock must be unchanged when a negative qty is rejected."""
    with pytest.raises(ValueError):
        inventory.reserve_stock("widget", -5)
    assert inventory.STOCK["widget"] == 100


def test_reserve_stock_zero_qty_raises_value_error():
    """Zero qty is also invalid and must raise ValueError."""
    with pytest.raises(ValueError):
        inventory.reserve_stock("widget", 0)


def test_reserve_stock_positive_qty_still_works():
    """Positive qty must still reduce stock correctly."""
    remaining = inventory.reserve_stock("widget", 10)
    assert remaining == 90
    assert inventory.STOCK["widget"] == 90
