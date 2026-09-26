"""Incident2Fix dashboard - visual front for the pipeline.

Run from repo root:
    py dashboard/app.py        (Windows)
    python dashboard/app.py    (macOS/Linux)
Open: http://127.0.0.1:5001

Reads demo-app/incidents/*.md and reports/*.md. The two human gates are
enforced by pipeline/run.py; decision buttons here record the reviewer's
decision (with comment) as an advisory log under reports/.
"""

import os
import re
from datetime import datetime

from flask import Flask, jsonify, render_template, request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INCIDENTS = os.path.join(ROOT, "demo-app", "incidents")
REPORTS = os.path.join(ROOT, "reports")

STAGES = [
    {"key": "TRIAGE", "agent": "Triage Agent",
     "desc": "Reads the incident, confirms severity, ranks suspect files."},
    {"key": "RCA", "agent": "Root-Cause Agent",
     "desc": "Reproduces the bug and isolates the faulty code."},
    {"key": "FIX", "agent": "Fix Agent",
     "desc": "Proposes a minimal diff for human review."},
    {"key": "APPLY", "agent": "Apply Patch",
     "desc": "Applies the approved diff - only after Gate 2 approval."},
    {"key": "TESTS", "agent": "Regression Test Agent",
     "desc": "Generates regression tests pinning the incident, runs the suite."},
]

app = Flask(__name__)

BOX_CHARS = "─━═│┌┐└┘├┤┬┴┼║╭╮╯╰"


def clean_snippet(text, max_lines=4, max_chars=260):
    """First meaningful lines of a Bob report, skipping TUI chrome."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if re.match(r"^[" + BOX_CHARS + r"\s]+$", s):
            continue
        if re.match(r"^(User|Tool) \(\d+\)", s):
            continue
        if s.startswith(("Tool:", "Args:", "- skill_name:", "- path:")):
            continue
        out.append(s)
        if len(out) >= max_lines:
            break
    snippet = " ".join(out)
    return snippet[:max_chars] + ("..." if len(snippet) > max_chars else "")


def parse_incident(iid):
    path = os.path.join(INCIDENTS, f"{iid}.md")
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    def field(name, default=""):
        m = re.search(r"\*\*" + name + r":\*\*\s*(.+)", text)
        return m.group(1).strip() if m else default
    title = iid
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if m:
        title = m.group(1).strip()
    summary = ""
    m = re.search(r"## Summary\n(.+?)(?:\n## |\Z)", text, re.S)
    if m:
        summary = " ".join(m.group(1).split())[:400]
    return {
        "id": iid,
        "title": title,
        "severity": field("Severity", "SEV-?"),
        "date": field("Date"),
        "summary": summary,
    }


def stage_info(iid, key):
    p = os.path.join(REPORTS, f"{key}-{iid}.md")
    if not os.path.exists(p):
        return {"status": "pending"}
    st = os.stat(p)
    with open(p, encoding="utf-8", errors="replace") as fh:
        content = fh.read()
    info = {
        "status": "done",
        "time": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
        "size_kb": round(st.st_size / 1024, 1),
        "snippet": clean_snippet(content),
    }
    if key == "TESTS":
        hits = re.findall(r"(\d+)\s+passed", content)
        if hits:
            info["tests_passed"] = int(hits[-1])
    return info


def gate_decision(iid, gate):
    """Previously recorded dashboard decision, if any."""
    for prefix in ("APPROVAL", "REJECTION"):
        p = os.path.join(REPORTS, f"{prefix}-GATE{gate}-{iid}.txt")
        if os.path.exists(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                parts = fh.read().split("\n", 1)
            return {
                "decision": "approved" if prefix == "APPROVAL" else "rejected",
                "comment": parts[1].strip() if len(parts) > 1 else "",
                "time": datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M"),
            }
    return None


def incident_payload(iid):
    inc = parse_incident(iid)
    stages = {s["key"]: stage_info(iid, s["key"]) for s in STAGES}
    done = sum(1 for s in stages.values() if s["status"] == "done")
    inc["stages"] = stages
    inc["progress"] = done
    inc["pipeline_status"] = (
        "Resolved" if stages["TESTS"]["status"] == "done"
        else "In progress" if done > 0 else "Open"
    )
    tests = stages["TESTS"].get("tests_passed")
    inc["tests_passed"] = tests
    inc["gate1"] = gate_decision(iid, "1")
    inc["gate2"] = gate_decision(iid, "2")
    return inc


def list_incidents():
    out = []
    if not os.path.isdir(INCIDENTS):
        return out
    for f in sorted(os.listdir(INCIDENTS)):
        m = re.match(r"(INCIDENT-\d+)\.md", f)
        if m:
            out.append(incident_payload(m.group(1)))
    return out


def parse_diff(iid):
    """Extract a unified diff from the FIX report, if one is embedded."""
    p = os.path.join(REPORTS, f"FIX-{iid}.md")
    if not os.path.exists(p):
        return {"status": "pending"}
    with open(p, encoding="utf-8", errors="replace") as fh:
        content = fh.read()
    if "@@" not in content and "diff --git" not in content:
        return {"status": "empty", "note": "No unified diff block found - see the full report."}
    lines, adds, dels, in_hunk = [], 0, 0, False
    for raw in content.splitlines():
        line = raw.rstrip("\n")
        if line.startswith("diff --git") or line.startswith("@@"):
            in_hunk = True
            lines.append({"t": "hunk", "text": line})
            continue
        if not in_hunk:
            continue
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            adds += 1
            lines.append({"t": "add", "text": line[1:]})
        elif line.startswith("-"):
            dels += 1
            lines.append({"t": "del", "text": line[1:]})
        elif line.startswith(" ") or not line.strip():
            lines.append({"t": "ctx", "text": line[1:] if line.startswith(" ") else line})
        else:
            in_hunk = False
    if not lines:
        return {"status": "empty", "note": "No unified diff block found - see the full report."}
    return {"status": "done", "additions": adds, "deletions": dels,
            "lines": lines[:400]}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/incidents")
def api_incidents():
    return jsonify(list_incidents())


@app.get("/api/report/<iid>/<stage>")
def api_report(iid, stage):
    if not re.fullmatch(r"INCIDENT-\d+", iid or ""):
        return {"error": "bad incident"}, 400
    if stage not in [s["key"] for s in STAGES]:
        return {"error": "bad stage"}, 400
    p = os.path.join(REPORTS, f"{stage}-{iid}.md")
    if not os.path.exists(p):
        return {"status": "pending"}
    with open(p, encoding="utf-8", errors="replace") as fh:
        content = fh.read()
    info = stage_info(iid, stage)
    return {"status": "done", "content": content,
            "time": info["time"], "size_kb": info["size_kb"]}


@app.get("/api/diff/<iid>")
def api_diff(iid):
    if not re.fullmatch(r"INCIDENT-\d+", iid or ""):
        return {"error": "bad incident"}, 400
    return jsonify(parse_diff(iid))


@app.post("/api/decision")
def api_decision():
    data = request.get_json(force=True) or {}
    iid, gate = data.get("incident"), str(data.get("gate"))
    decision, comment = data.get("decision"), (data.get("comment") or "").strip()[:500]
    if not re.fullmatch(r"INCIDENT-\d+", iid or ""):
        return {"error": "bad incident"}, 400
    if gate not in ("1", "2") or decision not in ("approved", "rejected"):
        return {"error": "bad request"}, 400
    os.makedirs(REPORTS, exist_ok=True)
    fname = f"{'APPROVAL' if decision == 'approved' else 'REJECTION'}-GATE{gate}-{iid}.txt"
    with open(os.path.join(REPORTS, fname), "w", encoding="utf-8") as fh:
        fh.write(f"{decision}\n{comment}\n")
    return {"ok": True}


if __name__ == "__main__":
    app.run(port=5001)
