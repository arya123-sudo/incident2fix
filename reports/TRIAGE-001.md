# TRIAGE-001: Checkout returns HTTP 500 for EUR currency

**Incident ID:** INCIDENT-001
**Date:** 2026-09-20
**Severity:** SEV-2
**Status:** Open

## Endpoint
`POST /checkout`

## Failure Signature
`KeyError: 'EUR'`

Raised at `app/currency.py:12` inside `convert()` when the currency code
passed by the caller is not a key in `SUPPORTED_CURRENCIES`.

**Full trace:**
```
File "app/main.py", line 15, in checkout
    return jsonify(orders.checkout(body)), 200
File "app/orders.py", line 13, in checkout
    total: float = currency.convert(discounted_total, order["currency"])
File "app/currency.py", line 12, in convert
    return amount * SUPPORTED_CURRENCIES[code]
KeyError: 'EUR'
```

The unhandled `KeyError` propagates up through `orders.checkout()` and is
caught by the bare `except Exception` in `main.py:checkout()`, which returns
HTTP 500.

## Suspect Files (ranked)

| Rank | File | Reason |
|------|------|--------|
| 1 | `demo-app/app/currency.py` | `SUPPORTED_CURRENCIES` dict contains only `USD`, `INR`, `GBP`. `convert()` does a bare dict lookup (`SUPPORTED_CURRENCIES[code]`), raising `KeyError` for any unlisted code such as `"EUR"`. **Root of the bug.** |
| 2 | `demo-app/app/orders.py` | Calls `currency.convert(discounted_total, order["currency"])` at line 13 with no guard against unsupported currencies; lets the exception bubble up. |
| 3 | `demo-app/app/main.py` | The `/checkout` handler at line 14–17 catches `Exception` and converts it to a 500. Correct behavior would require either the currency lookup to return a 4xx-worthy error or the handler to distinguish `KeyError` from fatal errors. |

## Reproduction Hypothesis

Sending any `POST /checkout` request where `"currency"` is a code absent from
`SUPPORTED_CURRENCIES` (currently `{"USD", "INR", "GBP"}`) causes
`currency.convert()` to raise `KeyError`, which the handler surfaces as HTTP 500.
Adding `"EUR"` (or any other ISO currency code) to `SUPPORTED_CURRENCIES` with
the correct exchange-rate multiplier will resolve the crash.

## Exact Payload / Steps to Reproduce

```bash
curl -X POST http://localhost:5000/checkout \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{"sku": "widget", "price": 49.99, "qty": 2}],
    "currency": "EUR",
    "discount_code": "SAVE10"
  }'
```

**Expected:** HTTP 200 with converted totals in EUR  
**Actual:** HTTP 500 `{"error": "'EUR'"}`
