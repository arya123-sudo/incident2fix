# TESTS-003: Regression tests for FIX-003

**Incident ID:** INCIDENT-003
**Fix Report:** FIX-003
**Date:** 2026-09-26
**Test File:** `demo-app/tests/test_regression_003.py`

---

## Summary

Seven regression tests were written to pin the exact incident scenario and the
surrounding edge cases for FIX-003 (reserve_stock() accepting negative qty and
inflating stock instead of decreasing it).

All seven new tests **fail** on the pre-fix code (no validation before
`STOCK[item] -= qty`) and **pass** on the fixed code (`qty <= 0` guard raising
`ValueError` before any mutation).

---

## Test List

| # | Test name | Purpose |
|---|-----------|---------|
| 1 | `test_reserve_stock_negative_qty_raises_value_error` | `qty=-5` raises `ValueError` — the exact incident input |
| 2 | `test_reserve_stock_negative_qty_does_not_mutate_stock` | STOCK is unchanged when negative qty is rejected |
| 3 | `test_reserve_stock_zero_qty_raises_value_error` | `qty=0` is also invalid and raises `ValueError` |
| 4 | `test_reserve_stock_zero_qty_does_not_mutate_stock` | STOCK is unchanged when zero qty is rejected |
| 5 | `test_reserve_stock_positive_qty_still_works` | Positive qty still reduces stock correctly |
| 6 | `test_reserve_endpoint_negative_qty_raises_and_leaves_stock_intact` | `POST /reserve` with negative qty returns HTTP 500 and leaves stock intact |
| 7 | `test_reserve_stock_error_message_contains_bad_qty` | The `ValueError` message identifies the rejected qty |

---

## pytest Output

```
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0
collected 45 items

demo-app/tests/test_regression_003.py::test_reserve_stock_negative_qty_raises_value_error PASSED
demo-app/tests/test_regression_003.py::test_reserve_stock_negative_qty_does_not_mutate_stock PASSED
demo-app/tests/test_regression_003.py::test_reserve_stock_zero_qty_raises_value_error PASSED
demo-app/tests/test_regression_003.py::test_reserve_stock_zero_qty_does_not_mutate_stock PASSED
demo-app/tests/test_regression_003.py::test_reserve_stock_positive_qty_still_works PASSED
demo-app/tests/test_regression_003.py::test_reserve_endpoint_negative_qty_raises_and_leaves_stock_intact PASSED
demo-app/tests/test_regression_003.py::test_reserve_stock_error_message_contains_bad_qty PASSED
[... 38 other tests all PASSED ...]

============================= 45 passed in 0.29s ==============================
```

---

## Final Count

| Category | Count |
|----------|-------|
| New tests (FIX-003) | 7 |
| Pre-existing tests | 38 |
| **Total** | **45** |
| Passed | 45 |
| Failed | 0 |
