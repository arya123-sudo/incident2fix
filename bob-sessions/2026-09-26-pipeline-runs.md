# Bob sessions - 2026-09-26 (first live end-to-end runs)

## Environment
- Bob Shell 2.0.5, Node v24.15.0, Windows 11, PowerShell
- Logged in as aryayaligar7@gmail.com (IBMid); headless `bob -p` auth via BOB_API_KEY
- Repo: incident2fix-submission (this repo), run from D:\incident2fix-submission

## Session 1 - project comprehension check
- **Goal:** verify Bob 2.0 works non-interactively against the repo
- **Command:** `bob -p "Explain what this project does"`
- **Bob's output:** accurate summary - 4-stage pipeline (triage -> RCA -> fix ->
  regression tests), 2 human gates, component table (pipeline/, .bob/skills/,
  demo-app/, dashboard/), mermaid flow diagram
- **Task ID:** 635f3845dd331ee95209d2ee71279dbb

## Session 2 - INCIDENT-001 (EUR checkout HTTP 500)
- **Goal:** full pipeline run: `py pipeline/run.py demo-app/incidents/INCIDENT-001.md`
- **Bob's role per stage (via `use_skill` tool):**
  - triage -> skill `incident-triage`
  - RCA -> skill `root-cause-analysis`
  - fix proposal -> skill `fix-generation`
  - patch apply (after human Gate 2) -> skill `fix-generation`
  - regression tests -> skill `regression-testing`
- **Human decisions:** Gate 1 (approve RCA) - approved; Gate 2 (approve diff) - approved
- **Result:** DONE; `py -m pytest demo-app/tests -q` -> **18 passed**
- **Reports:** reports/TRIAGE-INCIDENT-001.md, RCA-INCIDENT-001.md,
  FIX-INCIDENT-001.md, APPLY-INCIDENT-001.md, TESTS-INCIDENT-001.md

## Session 3 - INCIDENT-002 (silent discount bug)
- **Goal:** `py pipeline/run.py demo-app/incidents/INCIDENT-002.md`
- **Human decisions:** Gate 1 approved; Gate 2 approved
- **Result:** DONE, reports written for INCIDENT-002

## Session 4 - INCIDENT-003 (inventory corruption)
- **Goal:** `py pipeline/run.py demo-app/incidents/INCIDENT-003.md`
- **Human decisions:** Gate 1 approved; Gate 2 approved
- **Result:** DONE, reports written for INCIDENT-003

## Notes for judges
- Every stage's agent behavior is defined in `.bob/skills/<stage>/SKILL.md`;
  the orchestrator (`pipeline/run.py`) prepends the skill brief to each `bob -p` call.
- No code was changed without a human typing `y` at the two gates
  (enforced in `pipeline/run.py`, policy in `.bob/rules/pipeline-governance.md`).
- Screenshots: capture `bob -p` runs and the dashboard during the final
  recorded demo run; save PNGs in this folder.
