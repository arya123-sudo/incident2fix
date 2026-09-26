"""Currency conversion for order totals."""

SUPPORTED_CURRENCIES: dict[str, float] = {
    "USD": 1.0,
    "INR": 83.2,
    "GBP": 0.79,
}


def convert(amount: float, code: str) -> float:
    """Convert an amount from USD into the target currency."""
    return amount * SUPPORTED_CURRENCIES[code]
