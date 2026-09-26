"""In-memory stock inventory."""

STOCK: dict[str, int] = {"widget": 100, "gadget": 50}


def reserve_stock(item: str, qty: int) -> int:
    """Reserve qty units of item. Returns remaining stock."""
    STOCK[item] -= qty
    return STOCK[item]
