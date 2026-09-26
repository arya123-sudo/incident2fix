# INCIDENT-001: Checkout returns HTTP 500 for EUR currency

**Date:** 2026-09-20
**Severity:** SEV-2
**Status:** Open

## Summary
All `POST /checkout` requests with `"currency": "EUR"` fail with HTTP 500.
USD, INR, and GBP checkouts are unaffected.

## Impact
- 34 failed checkouts during 2026-09-20 14:00–18:30 UTC
- EU customers cannot complete purchases; estimated revenue at risk: ~€12,400

## Log excerpt (production)

```
2026-09-20 14:02:11,403 ERROR checkout-service pid=7712 req_id=a3f9c1 POST /checkout 500 in 12ms
Traceback (most recent call last):
  File "app/main.py", line 15, in checkout
    return jsonify(orders.checkout(body)), 200
  File "app/orders.py", line 13, in checkout
    total: float = currency.convert(discounted_total, order["currency"])
  File "app/currency.py", line 12, in convert
    return amount * SUPPORTED_CURRENCIES[code]
KeyError: 'EUR'
2026-09-20 14:02:11,404 INFO  checkout-service req_id=a3f9c1 responded {"error": "'EUR'"}, status=500
```

The same traceback repeats for every EUR checkout attempt (34 occurrences),
e.g. `req_id=9bd2e7` at 15:44:02, `req_id=c01a55` at 17:18:39.

## Request payload that triggered it

```json
{
  "items": [{"sku": "widget", "price": 49.99, "qty": 2}],
  "currency": "EUR",
  "discount_code": "SAVE10"
}
```

## Suspected cause
`app/currency.py` does a direct dict lookup against `SUPPORTED_CURRENCIES`,
which only defines USD, INR, and GBP. Any unsupported currency raises
`KeyError`, which the `/checkout` handler turns into a 500.
