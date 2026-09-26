"""Regression tests for FIX-001.

Incident: POST /checkout returns HTTP 500 for EUR currency (unhandled KeyError).
Root cause (RCA-001): currency.convert() used a bare dict subscript
    SUPPORTED_CURRENCIES[code] which raises KeyError for any unknown code.
Fix: replaced with .get() + explicit ValueError for unknown codes.

These tests FAIL on the pre-fix code (bare dict subscript) and
PASS on the fixed code (.get() + ValueError guard).
"""

import pytest

from app import currency
from app.main import create_app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    """Flask test client."""
    app = create_app()
    app.testing = True
    return app.test_client()


# ---------------------------------------------------------------------------
# Exact incident scenario — EUR raises ValueError, not KeyError
# ---------------------------------------------------------------------------


def test_convert_eur_raises_value_error_not_key_error():
    """convert() with 'EUR' must raise ValueError, not KeyError.

    Pre-fix: SUPPORTED_CURRENCIES['EUR'] → KeyError: 'EUR'
    Post-fix: rate is None → ValueError("Unsupported currency: 'EUR'")
    """
    with pytest.raises(ValueError, match="Unsupported currency"):
        currency.convert(100.0, "EUR")


def test_checkout_eur_returns_500_with_error_body(client):
    """POST /checkout with EUR must return HTTP 500 and a JSON error body."""
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
    assert "EUR" in body["error"]


# ---------------------------------------------------------------------------
# Edge cases around the fix
# ---------------------------------------------------------------------------


def test_convert_any_unknown_code_raises_value_error():
    """Any unsupported code must raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported currency"):
        currency.convert(50.0, "JPY")


def test_convert_supported_currencies_unaffected():
    """USD, INR, and GBP must still convert correctly after the fix."""
    assert currency.convert(100.0, "USD") == pytest.approx(100.0)
    assert currency.convert(100.0, "INR") == pytest.approx(8320.0)
    assert currency.convert(100.0, "GBP") == pytest.approx(79.0)


def test_convert_error_message_contains_bad_code():
    """The ValueError message must identify the rejected code."""
    with pytest.raises(ValueError, match="'XYZ'"):
        currency.convert(1.0, "XYZ")
