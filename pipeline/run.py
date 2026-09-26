"""Incident2Fix orchestrator.

Runs the four Bob 2.0 stages in order, enforcing the two human gates:

    incident -> triage -> RCA -> [GATE 1] -> fix diff -> [GATE 2] -> apply -> tests

Usage:
    python pipeline/run.py demo-app/incidents/INCIDENT-001.md [--yes]
"""

from __future__ import annotations

import argparse
import os
import re
import sys

from pipeline.bob_client import run_skill

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports")


def incident_id(path: str) -> str:
    m = re.search(r"(INCIDENT-\d+)", os.path.basename(path))
    if not m:
        raise ValueError(f"Cannot derive incident id from {path!r}")
    return m.group(1)


def gate(name: str, auto_yes: bool) -> bool:
    if auto_yes:
        print(f"[gate] {name}: auto-approved (--yes)")
        return True
    ans = input(f"[gate] {name} - approve? [y/N] ").strip().lower()
    return ans in ("y", "yes")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("incident", help="path to incident markdown")
    ap.add_argument("--yes", action="store_true", help="auto-approve both gates")
    args = ap.parse_args()

    iid = incident_id(args.incident)
    os.makedirs(REPORTS, exist_ok=True)

    print(f"== Incident2Fix: {iid} ==")

    print("\n[1/4] triage (Bob 2.0)...")
    triage = run_skill(
        "incident-triage",
        f"Triage the incident at {args.incident}. Repo root is {ROOT}.",
        ROOT,
    )
    with open(os.path.join(REPORTS, f"TRIAGE-{iid}.md"), "w") as f:
        f.write(triage)
    print(triage[:600])

    print("\n[2/4] root-cause analysis (Bob 2.0)...")
    rca = run_skill(
        "root-cause-analysis",
        f"Perform RCA using reports/TRIAGE-{iid}.md. Repo root is {ROOT}.",
        ROOT,
    )
    with open(os.path.join(REPORTS, f"RCA-{iid}.md"), "w") as f:
        f.write(rca)
    print(rca[:600])

    if not gate("GATE 1 - approve RCA, generate fix", args.yes):
        print("Stopped at gate 1.")
        return 2

    print("\n[3/4] fix generation (Bob 2.0)...")
    fix = run_skill(
        "fix-generation",
        f"Propose a fix using the approved reports/RCA-{iid}.md. Repo root is {ROOT}.",
        ROOT,
    )
    with open(os.path.join(REPORTS, f"FIX-{iid}.md"), "w") as f:
        f.write(fix)
    print(fix[:800])

    if not gate("GATE 2 - approve diff, apply patch", args.yes):
        print("Stopped at gate 2.")
        return 2

    print("\n[4/4] regression testing (Bob 2.0)...")
    tests = run_skill(
        "regression-testing",
        f"Generate and run regression tests for {iid} using reports/FIX-{iid}.md. Repo root is {ROOT}.",
        ROOT,
    )
    with open(os.path.join(REPORTS, f"TESTS-{iid}.md"), "w") as f:
        f.write(tests)
    print(tests[:600])

    print(f"\nDONE. Reports in {REPORTS}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
