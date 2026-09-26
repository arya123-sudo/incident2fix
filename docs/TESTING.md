# Testing strategy

## The baseline suite (`demo-app/tests/`) — 5 tests, green on buggy code

`test_smoke.py` is the **pre-fix baseline**. It deliberately exercises only
happy paths (exact-case discount codes, supported currencies, positive
quantities), so it passes on the pristine checkout with all three seeded
bugs present. That is the point: it proves the app works *except* for the
incidents, and it gives Bob's regression-test agent a green suite to extend.

Reproduce it:

```
pip install flask pytest
python -m pytest demo-app/tests -q     # 5 passed
```

`conftest.py` inserts `demo-app/` into `sys.path` (relative to the test
file), so no `PYTHONPATH` setup or package install is needed.

### Test → incident traceability

| Test | Baseline for | Why it passes pre-fix |
|---|---|---|
| `test_checkout_usd_with_save10` | INCIDENT-001 (EUR checkout 500) | USD is a supported currency; the bug only bites unsupported codes |
| `test_apply_discount_save10_exact_case` | INCIDENT-002 (code silently ignored) | Exact case works; the bug is other casings |
| `test_reserve_stock_decreases` | INCIDENT-003 (inventory corruption) | Positive qty works; the bug is negative qty |
| `test_discount_endpoint` | INCIDENT-002, endpoint level | Exact case via HTTP |
| `test_orders_checkout_no_discount_code` | INCIDENT-001 (currency conversion) | INR lookup succeeds; conversion math is correct |

Float assertions use `pytest.approx` so a future rounding change doesn't
break tests for the wrong reason.

## Bob-generated regression tests (`demo-app/regression_tests/`)

When the pipeline runs, Bob's regression-test agent writes new tests that
**pin each incident** — they fail on the buggy code and pass after the fix.
These are copied from real pipeline runs into `demo-app/regression_tests/`
(they are evidence, not hand-written).

Observed growth across the real runs:

| After | Suite size |
|---|---|
| Baseline | 5 passed |
| INCIDENT-001 | 18 passed |
| INCIDENT-001–003 | 45 passed |

Per-run evidence (including the tests Bob wrote) is in `reports/TESTS-*.md`.

Run them after the pipeline:

```
python -m pytest demo-app/regression_tests -q
```

Note: on the pristine buggy checkout these tests are *expected to fail* —
they assert post-fix behavior. That is why CI runs only the baseline suite.

## CI

`.github/workflows/ci.yml` runs the baseline suite on every push and PR.
It intentionally excludes `regression_tests/` (see above).

## Known gaps (flagged, not yet fixed)

- **Unvalidated request bodies** (`demo-app/app/main.py`): `/discount` does
  `body["code"]` and `/reserve` does `int(body["qty"])` with no validation,
  and `/checkout`'s generic `except Exception as e: return jsonify({"error":
  str(e)}), 500` leaks raw internal exception text to API callers. An
  incident-response tool should care about this; it is follow-up work, not
  one of the three seeded incidents.
- **Parametrize**: the discount cases are natural candidates for
  `@pytest.mark.parametrize`; left as-is to keep the baseline at 5 tests.
