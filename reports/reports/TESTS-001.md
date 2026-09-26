# TESTS-001: Regression tests for FIX-001

**Incident ID:** INCIDENT-001
**Fix Report:** FIX-001
**Date:** 2026-09-26
**Test File:** `demo-app/tests/test_regression_001.py`

---

## Summary

Five regression tests were written to pin the exact incident scenario and the
surrounding edge cases for FIX-001 (currency.convert() raising KeyError for
unsupported currencies).

All five new tests **fail** on the pre-fix code (bare `SUPPORTED_CURRENCIES[code]`
subscript) and **pass** on the fixed code (`.get()` + explicit `ValueError`).

---

## Test List

| # | Test name | Purpose |
|---|-----------|---------|
| 1 | `test_convert_eur_raises_value_error_not_key_error` | EUR must raise `ValueError`, not `KeyError` — the exact incident input |
| 2 | `test_checkout_eur_returns_500_with_error_body` | `POST /checkout` with EUR returns HTTP 500 with a JSON `error` field |
| 3 | `test_convert_any_unknown_code_raises_value_error` | Any unsupported code (e.g. JPY) also raises `ValueError` |
| 4 | `test_convert_supported_currencies_unaffected` | USD, INR, GBP still convert correctly after the fix |
| 5 | `test_convert_error_message_contains_bad_code` | The `ValueError` message identifies the rejected code |

---

## pytest Output

```
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0
collected 45 items

demo-app/tests/test_regression_001.py::test_convert_eur_raises_value_error_not_key_error PASSED
demo-app/tests/test_regression_001.py::test_checkout_eur_returns_500_with_error_body PASSED
demo-app/tests/test_regression_001.py::test_convert_any_unknown_code_raises_value_error PASSED
demo-app/tests/test_regression_001.py::test_convert_supported_currencies_unaffected PASSED
demo-app/tests/test_regression_001.py::test_convert_error_message_contains_bad_code PASSED
[... 40 other tests all PASSED ...]

============================= 45 passed in 0.29s ==============================
```

---

## Final Count

| Category | Count |
|----------|-------|
| New tests (FIX-001) | 5 |
| Pre-existing tests | 40 |
| **Total** | **45** |
| Passed | 45 |
| Failed | 0 |
