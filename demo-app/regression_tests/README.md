# Bob-generated regression tests

This folder holds the regression tests written by Bob's regression-test
agent during real pipeline runs. They are **evidence, not hand-written
code**: each test pins one of the three incidents (fails on the buggy
code, passes after the fix).

## Where the files come from

After running `py pipeline/run.py demo-app/incidents/INCIDENT-00X.md`,
copy the test files Bob added (everything in `demo-app/tests/` except
`test_smoke.py` and `conftest.py`) into this folder.

## Running them

```
python -m pytest demo-app/regression_tests -q
```

Run this **after** the pipeline has fixed the code. On the pristine buggy
checkout these tests are expected to fail — they assert post-fix behavior.
That is also why CI runs only the baseline suite in `demo-app/tests/`.

Observed suite growth in the real runs: 5 (baseline) → 18 (after
INCIDENT-001) → 45 (after all three). Per-run evidence, including the
tests Bob wrote, is in `reports/TESTS-*.md`.
