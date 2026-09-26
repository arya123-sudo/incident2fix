"""Regression tests for INCIDENT-002.

Incident: discount code "save10" silently applies no discount.
Root cause (RCA-002): apply_discount() passed the raw user-supplied code string
directly to a case-sensitive dict.get() lookup; DISCOUNT_CODES keys are stored
uppercase-only, so any lowercase/mixed-case variant was silently ignored.
Fix: code is normalised with .upper() before the lookup.

These tests FAIL on the pre-fix code (DISCOUNT_CODES.get(code, 0)) and
PASS on the fixed code (DISCOUNT_CODES.get(code.upper() if code else code, 0)).
"""

import pytest

from app import discounts
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
# Exact incident scenario — the failing input now behaves correctly
# ---------------------------------------------------------------------------


def test_apply_discount_lowercase_save10_gives_ten_percent():
    """'save10' (all lowercase) must apply the 10 % discount.

    On pre-fix code: DISCOUNT_CODES.get('save10', 0) → 0 → returns 100.0 (BUG).
    On fixed code:   DISCOUNT_CODES.get('SAVE10', 0) → 0.10 → returns 90.0.
    """
    result = discounts.apply_discount("save10", 100.0)
    assert result == pytest.approx(90.0)


def test_discount_endpoint_lowercase_save10_returns_ninety():
    """POST /discount with lowercase 'save10' must return discounted_total=90.0."""
    app = create_app()
    app.testing = True
    client = app.test_client()
    resp = client.post("/discount", json={"code": "save10", "subtotal": 100.0})
    assert resp.status_code == 200
    assert resp.get_json()["discounted_total"] == pytest.approx(90.0)


# ---------------------------------------------------------------------------
# Edge cases around the fix
# ---------------------------------------------------------------------------


def test_apply_discount_mixed_case_welcome20():
    """Mixed-case 'Welcome20' must apply the 20 % discount."""
    result = discounts.apply_discount("Welcome20", 200.0)
    assert result == pytest.approx(160.0)


def test_apply_discount_all_uppercase_unaffected():
    """Exact-uppercase codes must still work correctly after the fix."""
    assert discounts.apply_discount("SAVE10", 100.0) == pytest.approx(90.0)
    assert discounts.apply_discount("WELCOME20", 100.0) == pytest.approx(80.0)


def test_apply_discount_none_code_returns_full_subtotal():
    """None (no discount code) must still return the full subtotal unchanged."""
    assert discounts.apply_discount(None, 150.0) == pytest.approx(150.0)


def test_apply_discount_unknown_code_ignored():
    """An unrecognised code (even uppercased) returns the full subtotal."""
    assert discounts.apply_discount("BOGUS99", 100.0) == pytest.approx(100.0)


def test_apply_discount_empty_string_ignored():
    """An empty-string code does not crash and returns the full subtotal."""
    # "".upper() == "" which is not in DISCOUNT_CODES → treated as unknown
    result = discounts.apply_discount("", 100.0)
    assert result == pytest.approx(100.0)


def test_apply_discount_various_case_variants():
    """All case variants of SAVE10 must produce the same 10 % discount."""
    for variant in ("save10", "SAVE10", "Save10", "sAvE10"):
        result = discounts.apply_discount(variant, 100.0)
        assert result == pytest.approx(90.0), f"Failed for variant {variant!r}"
