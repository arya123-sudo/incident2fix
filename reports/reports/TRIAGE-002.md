# TRIAGE-002: Discount code "save10" silently applies no discount

**Incident ID:** INCIDENT-002
**Date:** 2026-09-19
**Severity:** SEV-3
**Status:** Open

## Endpoint
`POST /checkout` and `POST /discount`

## Failure Signature
Silent logic error — no exception, no error response. The discount multiplier
resolves to `0` (no discount) because `DISCOUNT_CODES.get(code, 0)` returns
the default `0` when the key is not found due to a case/whitespace mismatch.

- Input: `"discount_code": "save10"` (lowercase)
- `DISCOUNT_CODES` only has the key `"SAVE10"` (uppercase)
- `dict.get("save10", 0)` → `0` → `subtotal * (1 - 0)` → full price returned

## Suspect Files (ranked)

| Rank | File | Reason |
|------|------|--------|
| 1 | `demo-app/app/discounts.py` | `apply_discount()` at line 11 calls `DISCOUNT_CODES.get(code, 0)` with no normalization of `code` before the lookup. Any variant that differs in case or surrounding whitespace silently returns `0`. **Root of the bug.** |
| 2 | `demo-app/app/orders.py` | Passes `order.get("discount_code")` directly to `apply_discount()` at line 10–12 with no normalization. |
| 3 | `demo-app/app/main.py` | The `/discount` endpoint at line 22 passes `body["code"]` directly to `apply_discount()` with no normalization. |

## Reproduction Hypothesis

`apply_discount()` does a case-sensitive dict lookup. Any discount code that
does not exactly match a key in `DISCOUNT_CODES` (including differing only by
case or whitespace) silently applies zero discount. Normalizing the input
(`code.strip().upper()`) before the lookup will fix both affected endpoints.

## Exact Payload / Steps to Reproduce

**Via `/discount`:**
```bash
curl -X POST http://localhost:5000/discount \
  -H "Content-Type: application/json" \
  -d '{"code": "save10", "subtotal": 100}'
```
**Expected:** `{"discounted_total": 90.0}`  
**Actual:** `{"discounted_total": 100.0}`

**Via `/checkout`:**
```bash
curl -X POST http://localhost:5000/checkout \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{"sku": "widget", "price": 44.99, "qty": 2}],
    "currency": "USD",
    "discount_code": "save10"
  }'
```
**Expected:** `{"subtotal": 89.98, "discounted_total": 80.982, "total": 80.982, "currency": "USD"}`  
**Actual:** `{"subtotal": 89.98, "discounted_total": 89.98, "total": 89.98, "currency": "USD"}`

## Assumptions
- `" SAVE10 "` (with surrounding spaces) is also broken; the fix should include
  `.strip()` in addition to `.upper()`.
- `DISCOUNT_CODES` keys are canonically uppercase; normalization should be on
  the caller side, not by changing the dict keys.
