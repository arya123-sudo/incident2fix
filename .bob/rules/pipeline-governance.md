# Pipeline governance

Incident2Fix runs four stages in fixed order: triage -> root-cause analysis -> fix generation -> regression testing.

Two human gates are mandatory:
1. A human approves the RCA report before fix generation starts.
2. A human approves the exact diff before it is applied.

Agents never skip, reorder, or auto-approve gates. Every stage writes its report to `reports/` before the next begins. If any gate is rejected, the pipeline stops and records the reason.
