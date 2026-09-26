# Architecture

```
incident.md -> [Bob: triage] -> TRIAGE report -> [Bob: RCA] -> RCA report
  -> (human gate 1) -> [Bob: fix] -> diff -> (human gate 2) -> apply
  -> [Bob: tests] -> pytest suite -> DONE
```

- `.bob/skills/` - the four agent briefs Bob 2.0 executes, one per stage.
- `.bob/rules/` - governance (the two human gates) + Python standards, loaded on every run.
- `demo-app/` - seeded buggy Flask app, 3 incident reports, smoke tests.
- `pipeline/` - orchestrator: feeds each stage's inputs to Bob 2.0, enforces the gates, writes reports to `reports/`.
- Bob 2.0 is the engine of every stage. The orchestrator never hardcodes a diagnosis.

Demo: `python pipeline/run.py demo-app/incidents/INCIDENT-001.md`
