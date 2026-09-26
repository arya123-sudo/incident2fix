"""Order checkout logic."""

from app import currency, discounts


def checkout(order: dict) -> dict:
    """Compute order totals: subtotal -> discount -> currency conversion."""
    items: list[dict] = order.get("items", [])
    subtotal: float = sum(float(i["price"]) * int(i["qty"]) for i in items)
    discounted_total: float = discounts.apply_discount(
        order.get("discount_code"), subtotal
    )
    total: float = currency.convert(discounted_total, order["currency"])
    return {
        "subtotal": subtotal,
        "discounted_total": discounted_total,
        "total": total,
        "currency": order["currency"],
    }
