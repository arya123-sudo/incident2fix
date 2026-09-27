"""One-time fix: Gate 1 showed "Locked" on incidents whose later stages already ran
(e.g. Gate 2 rejected after Fix completed). The old code only treated
pipeline_status === "Resolved" as "gate was approved during the run".
Now it checks the stage after the gate directly, for any status.
Run once from the repo root:  py fix_gate1.py   Then delete this file."""

PATH = "dashboard/templates/index.html"

OLD = '''} else if (inc.pipeline_status === "Resolved") {
  // A rejected gate stops the pipeline, so a Resolved incident passed both gates
  // (approved in the terminal; no dashboard decision was recorded).'''

NEW = '''} else if ((inc.stages[n === 1 ? "FIX" : "APPLY"] || {}).status === "done") {
  // The pipeline stops at a rejected gate, so if the stage after this gate ran,
  // the gate was approved during the pipeline run (in the terminal — no
  // dashboard decision was recorded).'''

with open(PATH, encoding="utf-8") as f:
    text = f.read()

count = text.count(OLD)
if count != 1:
    raise SystemExit("Expected exactly 1 match, found %d — file may already be fixed." % count)

text = text.replace(OLD, NEW)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(text)

# sanity: braces still balance in the gateCard function
start = text.index("function gateCard(")
end = text.index("function renderGates(")
fn = text[start:end]
assert fn.count("{") == fn.count("}"), "brace mismatch in gateCard!"
print("OK: gateCard now keys off the downstream stage, not pipeline_status.")
