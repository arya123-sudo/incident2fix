"""Thin seam between the orchestrator and IBM Bob 2.0.

All agent work goes through run_skill(). Wire this to the real Bob 2.0
once its CLI/API access is available; the orchestrator never changes.
"""

from __future__ import annotations

import os
import subprocess


def run_skill(skill: str, prompt: str, workdir: str) -> str:
    """Run a .bob skill via Bob 2.0 and return the agent's output text.

    skill: one of incident-triage, root-cause-analysis, fix-generation,
           regression-testing (matches .bob/skills/<skill>/SKILL.md).

    Requires the BOB_API_KEY environment variable (Bob headless auth).
    """
    if not os.environ.get("BOB_API_KEY"):
        raise RuntimeError(
            "BOB_API_KEY is not set. In PowerShell: "
            '$env:BOB_API_KEY="paste-your-key-here"'
        )
    bob_bin = os.environ.get("BOB_CLI", "bob")
    skill_file = os.path.join(".bob", "skills", skill, "SKILL.md")
    with open(os.path.join(workdir, skill_file)) as f:
        brief = f.read()
    # Bob Shell's non-interactive form: bob -p "prompt".
    # The skill brief is prepended so Bob acts as that stage's agent.
    full_prompt = f"{brief}\n\n---\n\nTASK\n{prompt}\n"
    try:
        proc = subprocess.run(
            [bob_bin, "-p", full_prompt],
            capture_output=True,
            text=True,
            cwd=workdir,
            timeout=900,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Bob 2.0 CLI not found. Install Bob 2.0 and/or set BOB_CLI "
            "to its path, then re-run."
        )
    if proc.returncode != 0:
        raise RuntimeError(f"Bob 2.0 skill '{skill}' failed: {proc.stderr[:800]}")
    return proc.stdout
