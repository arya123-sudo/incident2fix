# Incident2Fix

Production error -> root cause -> fix -> regression tests, driven by IBM Bob 2.0 agents with human approval gates.

Built live during the IBM Bob 2.0 hackathon (lablab.ai, Sept 25-27 2026).

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r demo-app/requirements.txt
pytest demo-app/tests/ -q          # smoke tests: 5 passed
python pipeline/run.py demo-app/incidents/INCIDENT-001.md
```

## Layout

- `.bob/skills/` - Bob 2.0 agent briefs: triage, root-cause, fix, regression tests
- `.bob/rules/` - pipeline governance (human gates) + Python standards
- `demo-app/` - intentionally buggy Flask app + 3 incident reports
- `pipeline/` - orchestrator with the Bob 2.0 integration seam (`bob_client.py`)
- `docs/` - architecture

## Team
Two-person build: backend/Bob pipeline + frontend dashboard & submission.

## Dashboard

```bash
.venv/bin/python dashboard/app.py   # open http://127.0.0.1:5001
```

Incident cards, live stage tracker, gate approval buttons, and report viewer.

## Bob API key (required for the pipeline)

The pipeline calls Bob non-interactively (`bob -p`), which needs API-key auth:

```powershell
$env:BOB_API_KEY="paste-your-key-here"
```

Get the key from your IBM Bob account portal (log in with the same IBM ID),
or ask in the hackathon Discord. Never paste the key into chat or commit it.
