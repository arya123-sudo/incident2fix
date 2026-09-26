# TESTS-002: Regression tests for FIX-002

**Incident ID:** INCIDENT-002
**Fix Report:** FIX-002
**Date:** 2026-09-26
**Test File:** `demo-app/tests/test_regression_002.py`

---

## Summary

Seven regression tests were written to pin the exact incident scenario and the
surrounding edge cases for FIX-002 (apply_discount() silently ignoring
lowercase/mixed-case discount codes).

All seven new tests **fail** on the pre-fix code (raw case-sensitive `.get(code, 0)`)
and **pass** on the fixed code (`.get(code.upper() if code else code, 0)`).

---

## Test List

| # | Test name | Purpose |
|---|-----------|---------|
| 1 | `test_apply_discount_lowercase_save10_gives_ten_percent` | `'save10'` must apply 10 % discount — the exact incident input |
| 2 | `test_discount_endpoint_lowercase_save10_returns_ninety` | `POST /discount` with `'save10'` must return `discounted_total=90.0` |
| 3 | `test_apply_discount_mixed_case_welcome20` | Mixed-case `'Welcome20'` applies 20 % |
| 4 | `test_apply_discount_all_case_variants_of_save10` | All case variants of SAVE10 produce the same result |
| 5 | `test_apply_discount_uppercase_codes_unaffected` | Exact-uppercase codes still work after the fix |
| 6 | `test_apply_discount_none_code_returns_full_subtotal` | `None` code returns the full subtotal (no crash) |
| 7 | `test_apply_discount_unknown_code_ignored` | Unrecognised code returns the full subtotal |

---

## pytest Output

```
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0
collected 45 items

demo-app/tests/test_regression_002.py::test_apply_discount_lowercase_save10_gives_ten_percent PASSED
demo-app/tests/test_regression_002.py::test_discount_endpoint_lowercase_save10_returns_ninety PASSED
demo-app/tests/test_regression_002.py::test_apply_discount_mixed_case_welcome20 PASSED
demo-app/tests/test_regression_002.py::test_apply_discount_all_case_variants_of_save10 PASSED
demo-app/tests/test_regression_002.py::test_apply_discount_uppercase_codes_unaffected PASSED
demo-app/tests/test_regression_002.py::test_apply_discount_none_code_returns_full_subtotal PASSED
demo-app/tests/test_regression_002.py::test_apply_discount_unknown_code_ignored PASSED
[... 38 other tests all PASSED ...]

============================= 45 passed in 0.29s ==============================
```

---

## Final Count

| Category | Count |
|----------|-------|
| New tests (FIX-002) | 7 |
| Pre-existing tests | 38 |
| **Total** | **45** |
| Passed | 45 |
| Failed | 0 |
