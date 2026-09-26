"""Smoke tests for the demo app.

These tests deliberately PASS on the buggy code: they exercise only the
happy paths (exact-case discount codes, supported currencies, positive
quantities). The seeded incidents under ../incidents describe the known bugs.
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
    assert body["subtotal"] == 200.0
    assert body["discounted_total"] == 180.0
    assert body["total"] == 180.0
    assert body["currency"] == "USD"


def test_apply_discount_save10_exact_case():
    assert discounts.apply_discount("SAVE10", 100) == 90.0


def test_reserve_stock_decreases(client):
    resp = client.post("/reserve", json={"item": "widget", "qty": 5})
    assert resp.status_code == 200
    assert resp.get_json()["remaining"] == 95
    assert inventory.STOCK["widget"] == 95


def test_discount_endpoint(client):
    resp = client.post("/discount", json={"code": "SAVE10", "subtotal": 100})
    assert resp.status_code == 200
    assert resp.get_json()["discounted_total"] == 90.0


def test_orders_checkout_no_discount_code():
    result = orders.checkout(
        {
            "items": [{"sku": "gadget", "price": 50.0, "qty": 1}],
            "currency": "INR",
        }
    )
    assert result["subtotal"] == 50.0
    assert result["discounted_total"] == 50.0
    assert result["total"] == 50.0 * 83.2
