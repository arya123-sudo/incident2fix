# TRIAGE-003: Inventory anomaly — negative reservation inflated stock

**Incident ID:** INCIDENT-003
**Date:** 2026-09-18
**Severity:** SEV-3
**Status:** Open

## Endpoint
`POST /reserve`

## Failure Signature
Silent logic error — no exception, no error response. A negative `qty` value
is accepted without validation, causing stock to *increase* instead of decrease.

- Input: `{"item": "widget", "qty": -5}` (negative quantity)
- `reserve_stock()` computes `STOCK["widget"] -= -5` → `100 - (-5)` = `105`
- Response: `{"remaining": 105}` — stock inflated silently

## Suspect Files (ranked)

| Rank | File | Reason |
|------|------|--------|
| 1 | `demo-app/app/inventory.py` | `reserve_stock()` at line 8 does `STOCK[item] -= qty` with no validation of `qty` (must be positive) and no validation of `item` (must exist in `STOCK`). A negative `qty` inflates stock; an unknown `item` raises an unhandled `KeyError`. **Root of the bug.** |
| 2 | `demo-app/app/main.py` | The `/reserve` handler at line 28 casts `body["qty"]` to `int` but performs no range check before passing it to `reserve_stock()`. |

## Reproduction Hypothesis

`reserve_stock()` applies no guard against non-positive quantities. Passing
`qty <= 0` silently mutates `STOCK` in the wrong direction. Adding a
validation check (`if qty <= 0: raise ValueError`) before the subtraction will
prevent stock inflation. An additional guard for unknown items
(`if item not in STOCK: raise KeyError`) prevents a bare `KeyError` from
propagating as HTTP 500.

## Exact Payload / Steps to Reproduce

```bash
# Check initial stock (widget = 100)
# Then make a reservation with a negative quantity:
curl -X POST http://localhost:5000/reserve \
  -H "Content-Type: application/json" \
  -d '{"item": "widget", "qty": -5}'
```
**Expected:** HTTP 400 (invalid quantity) or similar validation error  
**Actual:** HTTP 200 `{"remaining": 105}` — stock inflated from 100 to 105

## Assumptions
- Zero quantity (`qty: 0`) is equally invalid and should be rejected.
- The fix should return HTTP 400 (not 500) for invalid input, keeping the 500
  path reserved for genuine server-side failures.
- `STOCK` is in-memory only; the in-memory state persists for the process
  lifetime, so the inflated value affects all subsequent reads until restart.
