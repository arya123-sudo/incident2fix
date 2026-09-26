"""Discount code handling."""

DISCOUNT_CODES: dict[str, float] = {
    "SAVE10": 0.10,
    "WELCOME20": 0.20,
}


def apply_discount(code: str | None, subtotal: float) -> float:
    """Apply a discount code to a subtotal. Unknown codes are ignored."""
    return subtotal * (1 - DISCOUNT_CODES.get(code, 0))
