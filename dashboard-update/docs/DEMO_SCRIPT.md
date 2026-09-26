# Demo video script (2-3 min)

Record the terminal on the left, the dashboard (http://127.0.0.1:5001) on the right.
Run the pipeline from a fresh clone so all three incidents are still buggy.

- **0:00** "Production incidents wake engineers at 3am. Incident2Fix lets IBM Bob 2.0 agents do the toil — triage, root cause, fix, regression tests — while humans keep the two decisions that matter."
- **0:20** Show INCIDENT-001: "EUR checkouts return HTTP 500. 34 failed checkouts." Open the dashboard — incident card shows SEV-2, Open, 0/5 stages.
- **0:35** Run `py pipeline/run.py demo-app/incidents/INCIDENT-001.md`. "Bob's triage agent reads the incident, ranks suspect files." Dashboard timeline fills in live.
- **0:55** "The RCA agent finds it: unguarded dict lookup in currency.py line 12 — and proves it with a reproduction script."
- **1:10** GATE 1: type `y` in the terminal after reviewing the RCA. "No fix is generated until a human approves the diagnosis."
- **1:25** "Bob proposes a minimal diff." Show the dashboard FIX tab — green/red diff view.
- **1:35** Rejection demo (15s): at Gate 2, type `N`. "A rejected patch touches nothing — the human is really in control." Then re-run and approve to continue. (Optional if short on time — one clean approval run is enough.)
- **1:50** GATE 2: type `y`. "No code changes without a human saying go." Patch applied.
- **2:00** "Bob writes regression tests pinning the incident and runs the whole suite — 18 passed." Dashboard shows Resolved, timeline complete.
- **2:20** Flip through INCIDENT-002 (silent discount bug) and INCIDENT-003 (inventory corruption) on the dashboard. "Three incidents, same pipeline — 45 tests green."
- **2:40** Close: "Incident2Fix: agents do the work, humans make the calls."

## Dashboard shots to capture

- Incident cards with severity badges and progress bars (before the run).
- Evidence timeline filling in stage by stage.
- Gate 2 card with the diff stats and Approve/Reject buttons.
- FIX tab diff view (green/red).
- Final state: all cards Resolved, header stats (3 incidents, 45 tests passing).

## Checklist before recording

- Fresh clone (buggy code), `pip install flask pytest` done.
- `$env:BOB_API_KEY` set in the recording terminal — never show the key on screen.
- Dashboard running on port 5001.
- Terminal font large enough to read at 1080p.
