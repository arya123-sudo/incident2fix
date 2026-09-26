"""Smoke tests for the demo app — the pre-fix baseline.

These tests deliberately PASS on the buggy code: they exercise only the
happy paths (exact-case discount codes, supported currencies, positive
quantities). Each test notes which seeded incident it is the baseline for,
so the test -> incident link is explicit.

Seeded incidents (demo-app/incidents/):
- INCIDENT-001: checkout in EUR returns HTTP 500 (currency.py:12,
  unguarded SUPPORTED_CURRENCIES[code] lookup)
- INCIDENT-002: discount code silently ignored when not exact case
  ("save10" -> DISCOUNT_CODES.get(code, 0) -> no discount, no error)
- INCIDENT-003: negative reserve quantity corrupts inventory
  (inventory.py:8, STOCK[item] -= qty with no validation)

Bob's regression-test agent generates the post-fix tests; those live in
demo-app/regression_tests/ (copied from real pipeline runs), not here.
"""

import pytest

from app import discounts, inventory, orders
from app.main import create_app


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
    app = create_app()
    app.testing = True
    return app.test_client()


def test_checkout_usd_with_save10(client):
    """Baseline for INCIDENT-001: checkout works on a supported currency.

    Passes pre-fix because USD is in SUPPORTED_CURRENCIES; the bug only
    bites unsupported codes (EUR -> KeyError -> HTTP 500).
    """
    resp = client.post(
        "/checkout",
        json={
            "items": [{"sku": "widget", "price": 100.0, "qty": 2}],
            "currency": "USD",
            "discount_code": "SAVE10",
        },
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["subtotal"] == pytest.approx(200.0)
    assert body["discounted_total"] == pytest.approx(180.0)
    assert body["total"] == pytest.approx(180.0)
    assert body["currency"] == "USD"


def test_apply_discount_save10_exact_case():
    """Baseline for INCIDENT-002: exact-case code applies the discount.

    Passes pre-fix; the bug is that any other casing is silently ignored.
    """
    assert discounts.apply_discount("SAVE10", 100) == pytest.approx(90.0)


def test_reserve_stock_decreases(client):
    """Baseline for INCIDENT-003: reserving a positive qty reduces stock.

    Passes pre-fix; the bug is that a negative qty corrupts STOCK.
    """
    resp = client.post("/reserve", json={"item": "widget", "qty": 5})
    assert resp.status_code == 200
    assert resp.get_json()["remaining"] == 95
    assert inventory.STOCK["widget"] == 95


def test_discount_endpoint(client):
    """Baseline for INCIDENT-002 at the endpoint level (exact case)."""
    resp = client.post("/discount", json={"code": "SAVE10", "subtotal": 100})
    assert resp.status_code == 200
    assert resp.get_json()["discounted_total"] == pytest.approx(90.0)


def test_orders_checkout_no_discount_code():
    """Baseline for INCIDENT-001: currency conversion on a supported code.

    INR converts at 83.2; passes pre-fix because the lookup succeeds.
    """
    result = orders.checkout(
        {
            "items": [{"sku": "gadget", "price": 50.0, "qty": 1}],
            "currency": "INR",
        }
    )
    assert result["subtotal"] == pytest.approx(50.0)
    assert result["discounted_total"] == pytest.approx(50.0)
    assert result["total"] == pytest.approx(50.0 * 83.2)
