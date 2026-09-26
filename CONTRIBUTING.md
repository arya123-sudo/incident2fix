# Contributing

## Running the tests

```bash
pip install flask pytest
python -m pytest demo-app/tests -q   # 5 baseline tests, green on the buggy checkout
```

## Adding a new incident

1. Write the incident report in `demo-app/incidents/INCIDENT-00X.md`
   (severity, symptoms, reproduction steps).
2. Seed the bug in `demo-app/app/` — keep it small and realistic.
3. Add a happy-path test to `demo-app/tests/test_smoke.py` that passes
   *despite* the bug, and note which incident it is the baseline for
   (see `docs/TESTING.md` for the traceability convention).
4. Run the pipeline: `py pipeline/run.py demo-app/incidents/INCIDENT-00X.md`
   (needs `$env:BOB_API_KEY`), approving both gates.
5. Copy the test files Bob generated into `demo-app/regression_tests/`
   (everything except `test_smoke.py`/`conftest.py`) — they are evidence
   of the run, not hand-written code.

## Pull requests

- Keep the baseline suite green: CI runs `demo-app/tests` on every push.
- Don't commit `reports/` noise from partial runs — only complete,
  human-approved runs.
- Never commit API keys, `.env` files, or credentials. Ever.
