#!/usr/bin/env python3
"""Lioreal Workshop Agent v0.1.

A dependency-light, local-first scaffold that turns a bounded task into an
inspectable run record. It does not call providers, mutate Git, deploy, or touch
production. Those keys are added deliberately and reviewably.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "workshop" / "runs"
NOW_FILE = ROOT / "workshop" / "NOW.md"

ALLOWED_RISK_CLASSES = {
    "read_only",
    "reviewable_write",
    "steward_required",
    "forbidden",
}


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


@dataclass
class AgentRun:
    run_key: str
    task: str
    mode: str
    risk_class: str
    status: str = "planned"
    branch_name: str | None = None
    starting_commit: str | None = None
    ending_commit: str | None = None
    started_at: str = field(default_factory=lambda: now_iso())
    finished_at: str | None = None
    checks: list[dict[str, Any]] = field(default_factory=list)
    blocker: str | None = None
    summary: str | None = None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_command(command: list[str]) -> tuple[int, str]:
    try:
        process = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, str(exc)
    output = (process.stdout + process.stderr).strip()
    return process.returncode, output


def git_value(*args: str) -> str | None:
    code, output = run_command(["git", *args])
    return output.splitlines()[0] if code == 0 and output else None


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def inspect_workspace() -> list[CheckResult]:
    checks: list[CheckResult] = []

    checks.append(
        CheckResult(
            "NOW.md exists",
            NOW_FILE.exists(),
            str(NOW_FILE.relative_to(ROOT)),
        )
    )

    charter = ROOT / "agent" / "CHARTER.md"
    checks.append(
        CheckResult(
            "Agent charter exists",
            charter.exists(),
            str(charter.relative_to(ROOT)),
        )
    )

    journal = ROOT / "workshop" / "journal" / "0000-the-workshop-exists.md"
    checks.append(
        CheckResult(
            "Workshop Journal is open",
            journal.exists(),
            str(journal.relative_to(ROOT)),
        )
    )

    migration = ROOT / "supabase" / "migrations" / "202607200001_lioreal_workshop_agent.sql"
    migration_ok = migration.exists() and "create table public.agent_runs" in migration.read_text(
        encoding="utf-8"
    )
    checks.append(
        CheckResult(
            "Workshop lineage migration exists",
            migration_ok,
            str(migration.relative_to(ROOT)),
        )
    )

    code, output = run_command([sys.executable, "-m", "py_compile", str(Path(__file__))])
    checks.append(
        CheckResult(
            "Agent scaffold compiles",
            code == 0,
            output or "py_compile passed",
        )
    )

    return checks


def write_run(run: AgentRun) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_DIR / f"{run.run_key}.json"
    payload = asdict(run)
    payload["evidence_sha256"] = sha256_text(json.dumps(payload, sort_keys=True))
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def execute(task: str, mode: str, risk_class: str) -> tuple[AgentRun, Path]:
    if risk_class not in ALLOWED_RISK_CLASSES:
        raise ValueError(f"Unknown risk class: {risk_class}")

    run = AgentRun(
        run_key=f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
        task=task,
        mode=mode,
        risk_class=risk_class,
        branch_name=git_value("branch", "--show-current"),
        starting_commit=git_value("rev-parse", "HEAD"),
    )

    if risk_class == "forbidden":
        run.status = "blocked"
        run.blocker = "The requested operation is forbidden by the Agent charter."
    elif risk_class == "steward_required" and mode != "steward":
        run.status = "blocked"
        run.blocker = "This operation requires Steward Mode and explicit approval."
    else:
        run.status = "running"
        checks = inspect_workspace()
        run.checks = [asdict(check) for check in checks]
        failures = [check for check in checks if not check.ok]
        if failures:
            run.status = "failed"
            run.summary = f"{len(failures)} validation check(s) failed."
        else:
            run.status = "completed"
            run.summary = "Workspace inspection completed; foundational agent artifacts are present."

    run.ending_commit = git_value("rev-parse", "HEAD")
    run.finished_at = now_iso()
    path = write_run(run)
    return run, path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a bounded Lioreal workshop inspection.")
    parser.add_argument("--task", default="Inspect Lioreal Workshop Agent foundation")
    parser.add_argument("--mode", choices=("workshop", "steward"), default="workshop")
    parser.add_argument(
        "--risk-class",
        choices=sorted(ALLOWED_RISK_CLASSES),
        default="read_only",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        run, path = execute(args.task, args.mode, args.risk_class)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(asdict(run), indent=2, sort_keys=True))
    print(f"Evidence: {path.relative_to(ROOT)}")
    return 0 if run.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
