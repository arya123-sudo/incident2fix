"""Incident2Fix dashboard - visual front for the pipeline.

Run:  ../.venv/bin/python dashboard/app.py   (from repo root: .venv/bin/python dashboard/app.py)
Open: http://127.0.0.1:5001
Reads incident files and generated reports; approval buttons record
human gate decisions as files under reports/.
"""

import os
import re

from flask import Flask, jsonify, render_template, request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INCIDENTS = os.path.join(ROOT, "demo-app", "incidents")
REPORTS = os.path.join(ROOT, "reports")
STAGES = ("TRIAGE", "RCA", "FIX", "TESTS")

app = Flask(__name__)


def incident_list():
    out = []
    for f in sorted(os.listdir(INCIDENTS)):
        m = re.match(r"(INCIDENT-\d+)\.md", f)
        if not m:
            continue
        iid = m.group(1)
        title = iid
        with open(os.path.join(INCIDENTS, f)) as fh:
            for line in fh:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
        stages = {s: os.path.exists(os.path.join(REPORTS, f"{s}-{iid}.md")) for s in STAGES}
        out.append({"id": iid, "title": title, "stages": stages})
    return out


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/incidents")
def api_incidents():
    return jsonify(incident_list())


@app.get("/api/report/<iid>/<stage>")
def api_report(iid, stage):
    if stage not in STAGES:
        return {"error": "bad stage"}, 400
    p = os.path.join(REPORTS, f"{stage}-{iid}.md")
    if not os.path.exists(p):
        return {"status": "pending"}
    with open(p) as fh:
        return {"status": "done", "content": fh.read()}


@app.post("/api/approve")
def api_approve():
    data = request.get_json(force=True) or {}
    iid, gate = data.get("incident"), data.get("gate")
    if gate not in ("GATE1", "GATE2") or not iid:
        return {"error": "bad request"}, 400
    os.makedirs(REPORTS, exist_ok=True)
    with open(os.path.join(REPORTS, f"APPROVAL-{gate}-{iid}.txt"), "w") as fh:
        fh.write("approved\n")
    return {"ok": True}


if __name__ == "__main__":
    app.run(port=5001, debug=True)
