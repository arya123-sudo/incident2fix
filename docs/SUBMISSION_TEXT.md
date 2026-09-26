# lablab.ai submission — draft text (fill in video link before submitting)

## Project name
Incident2Fix

## Tagline
Production error → root cause → fix → regression tests, with humans in control.

## Description (paste into lablab.ai)

**The problem.** Production incidents wake engineers at 3am: read the alert,
find the root cause, write a fix, make sure nothing else breaks. It's toil —
repetitive, stressful, and exactly the kind of work agents should do. But no
team will let an agent push code unsupervised.

**What we built.** Incident2Fix is an agentic incident-response pipeline driven
by **IBM Bob 2.0**. Given a production incident report, four Bob agents work
the case:

1. **Triage Agent** — reads the incident, confirms severity, ranks suspect files
2. **Root-Cause Agent** — reproduces the bug, isolates the faulty code
3. **Fix Agent** — proposes a minimal diff
4. **Regression Test Agent** — generates tests pinning the incident and runs the suite

**Humans make the two calls that matter.** Gate 1: approve the RCA before any
fix is generated. Gate 2: approve the diff before any code is touched. Reject
either one and the pipeline stops with zero changes — demonstrated in the video.

**Why Bob 2.0.** Every stage runs as a Bob skill (`.bob/skills/`), invoked
non-interactively via `bob -p`. The orchestrator never hardcodes a diagnosis;
Bob reasons over the incident, the code, and prior stage reports. Governance
lives in `.bob/rules/`: no code change without a human `y` at both gates.

**Proof it works.** Three seeded production incidents (EUR checkout 500s,
silent discount bug, inventory corruption) run end-to-end in the video: Bob
triages, finds each root cause, proposes patches a human approves, and grows
the test suite from 5 baseline tests to **45 passing**. Every Bob output is
kept as an evidence trail in `reports/` and viewable in the dashboard —
including a green/red diff view of each proposed fix.

**Try it:** clone the repo, `pip install flask pytest`,
`py pipeline/run.py demo-app/incidents/INCIDENT-001.md` (needs a Bob API key),
and open the dashboard at `http://127.0.0.1:5001`.

## Links
- GitHub: https://github.com/arya123-sudo/incident2fix
- Demo video: (paste YouTube unlisted link here)

## Differentiation one-liner
Not just AI for incidents — an auditable agent that turns incidents into
tested code fixes, with humans in control.

## Pre-submit checklist
- [ ] Demo video recorded; YouTube unlisted link pasted above and in README
- [ ] Dashboard screenshot embedded in README (replaces placeholder)
- [ ] `bob-sessions/` run summaries present (2026-09-26 runs committed)
- [ ] Rechecked official lablab.ai rules and exact deadline before submitting
