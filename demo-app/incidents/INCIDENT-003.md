# INCIDENT-003: Inventory anomaly — negative reservation inflated stock

**Date:** 2026-09-18 (warehouse ops alert)
**Severity:** SEV-3
**Status:** Open

## Summary
After a `POST /reserve` request with `qty: -5` for item `"widget"`, the
stock level for widget **increased** from 100 to 105 instead of decreasing.

## Timeline
- 2026-09-18 09:12:04 UTC — `/reserve {"item": "widget", "qty": -5}`
  responded `{"remaining": 105}`
- 2026-09-18 09:12:05 UTC — warehouse dashboard showed widget stock jumping
  from 100 to 105

## Impact
- Inventory counts no longer trustworthy; 1 SKU affected so far
- A caller can arbitrarily inflate stock with negative quantities
- No validation errors are returned; the operation "succeeds" silently

## Reproduction

```
POST /reserve {"item": "widget", "qty": -5}  ->  {"remaining": 105}
```

## Suspected cause
`app/inventory.py` `reserve_stock()` does `STOCK[item] -= qty` with no
validation of the quantity (or the item), so a negative qty inflates stock.
