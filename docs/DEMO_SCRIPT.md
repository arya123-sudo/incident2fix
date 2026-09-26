# Demo video script (2-3 min)

Record the terminal on the left, the dashboard (http://127.0.0.1:5001) on the right.

> Presenter note — gate timing (don't say on camera): the pipeline checks the
> dashboard's decision once when it reaches each gate, so click Approve while
> Bob is still working the previous stage. It won't pause mid-run waiting for
> a click — the terminal prompt is the fallback if no dashboard decision exists
> yet. Don't claim "live pause and resume" on stage.

- **0:00** "Production incidents wake engineers at 3am. Incident2Fix lets IBM Bob 2.0 agents do the toil - triage, root cause, fix, regression tests - while humans keep the two decisions that matter."
- **0:20** Show INCIDENT-001: "EUR checkouts return HTTP 500. 34 failed checkouts."
- **0:35** Run `python pipeline/run.py demo-app/incidents/INCIDENT-001.md`. "Bob's triage agent reads the incident, ranks suspect files."
- **0:55** "The RCA agent finds it: unguarded dict lookup in currency.py line 12 - and proves it with a reproduction script."
- **1:10** GATE 1: click Approve on the dashboard. "No fix is generated until a human approves the diagnosis."
- **1:25** "Bob proposes a minimal diff: add EUR, and raise a clear error for unknown currencies instead of KeyError."
- **1:40** GATE 2: approve the diff. "No code changes without a human saying go."
- **1:55** "Bob writes regression tests pinning the incident and runs the whole suite - 18 passed."
- **2:15** Flip through the other two incidents on the dashboard (silent discount bug, inventory corruption).
- **2:35** Close: "Incident2Fix: agents do the work, humans make the calls."
