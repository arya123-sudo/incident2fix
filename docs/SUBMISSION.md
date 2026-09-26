# lablab.ai submission draft

**Title:** Incident2Fix
**Tagline:** Production error → root cause → fix → regression tests. Bob 2.0 agents do the toil; humans keep the two decisions that matter.

## Description
Incident2Fix is an agentic incident-response pipeline powered by IBM Bob 2.0. Feed it a production incident report and four specialized Bob agents take over: triage ranks the suspect files, root-cause analysis pinpoints the exact defect and proves it with a reproduction script, fix generation proposes a minimal diff, and regression testing writes incident-specific tests and runs the full suite. Two human gates - RCA approval and diff approval - guarantee no code ever changes without a human saying go.

Built on a seeded buggy Flask app with three realistic incidents: a EUR checkout crash (KeyError), a silently-ignored discount code, and inventory corruption via negative quantities.

## Judging criteria
- **Application of Technology:** every stage is a Bob 2.0 agent driven by `.bob/skills/` briefs; Bob Shell (`bob -p`) is the pipeline engine.
- **Presentation:** live dashboard + 2-3 min demo video walking the full pipeline.
- **Business Value:** cuts incident response from hours of toil to minutes of supervision; every fix ships with regression tests.
- **Originality:** human gates as first-class pipeline stages, not an afterthought.

## Links
- GitHub repo: <TODO>
- Demo video: <TODO>
