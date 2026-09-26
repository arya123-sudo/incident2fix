# INCIDENT-002: Discount code "save10" silently applies no discount

**Date:** 2026-09-19 (customer support ticket #5823)
**Severity:** SEV-3
**Status:** Open

## Summary
Customers using the discount code **"save10"** (lowercase, as printed in the
marketing email blast of 2026-09-15) are charged full price. The code is
silently ignored — no error is returned and the checkout completes with no
discount applied.

## Customer report
> "I used the SAVE10 code from your email and my total didn't change.
>  I was charged $89.98 instead of $80.98."

## Example order

```json
{
  "items": [{"sku": "widget", "price": 44.99, "qty": 2}],
  "currency": "USD",
  "discount_code": "save10"
}
```

**Observed response:**
```json
{"subtotal": 89.98, "discounted_total": 89.98, "total": 89.98, "currency": "USD"}
```

**Expected response:**
```json
{"subtotal": 89.98, "discounted_total": 80.982, "total": 80.982, "currency": "USD"}
```

## Notes
- No crash, no traceback — this is a silent logic bug. Only the exact-case
  code `"SAVE10"` works; `"save10"`, `"Save10"`, or `" SAVE10 "` apply nothing.
- `/discount` behaves the same way: `POST {"code": "save10", "subtotal": 100}`
  returns `{"discounted_total": 100.0}` instead of `90.0`.
- Suspected cause: `app/discounts.py` looks up the raw code string in
  `DISCOUNT_CODES` with no case/whitespace normalization.
