#!/usr/bin/env python3
"""Lioreal caretaker services.

Provides bounded self-healing, guarded Git fast-forward updates with rollback,
and SMTP email reporting. Secrets are read from environment variables only.
No canonical content is rewritten by the healing routine.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import smtplib
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "workshop" / "runs"
QUARANTINE_DIR = ROOT / "workshop" / "quarantine"


@dataclass
class Action:
    kind: str
    target: str
    status: str
    detail: str


@dataclass
class CaretakerReport:
    operation: str
    status: str = "running"
    started_at: str = field(default_factory=lambda: now_iso())
    finished_at: str | None = None
    checkpoint: str | None = None
    actions: list[dict[str, Any]] = field(default_factory=list)
    notification: str | None = None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(command: list[str], timeout: int = 60) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, str(exc)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def git(*args: str) -> tuple[int, str]:
    return run(["git", *args])


def record(report: CaretakerReport) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RUNS_DIR / f"caretaker-{stamp}-{report.operation}.json"
    path.write_text(json.dumps(asdict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def validate() -> tuple[bool, str]:
    required = [
        ROOT / "agent" / "CHARTER.md",
        ROOT / "agent" / "lioreal_agent.py",
        ROOT / "workshop" / "NOW.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        return False, "Missing required files: " + ", ".join(missing)
    code, output = run([sys.executable, "-m", "py_compile", str(ROOT / "agent" / "lioreal_agent.py"), str(Path(__file__))])
    return code == 0, output or "compile and contract checks passed"


def heal() -> CaretakerReport:
    report = CaretakerReport(operation="heal")

    for directory in (RUNS_DIR, QUARANTINE_DIR):
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            report.actions.append(asdict(Action("create_directory", str(directory.relative_to(ROOT)), "repaired", "Created missing derived directory.")))
        else:
            report.actions.append(asdict(Action("check_directory", str(directory.relative_to(ROOT)), "healthy", "Directory exists.")))

    for candidate in RUNS_DIR.glob("*.json"):
        try:
            json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            destination = QUARANTINE_DIR / candidate.name
            shutil.move(str(candidate), destination)
            report.actions.append(asdict(Action("quarantine_generated_record", str(candidate.relative_to(ROOT)), "repaired", f"Moved malformed generated record to {destination.relative_to(ROOT)}: {exc}")))

    healthy, detail = validate()
    report.actions.append(asdict(Action("validate", "agent foundation", "healthy" if healthy else "degraded", detail)))
    report.status = "completed" if healthy else "degraded"
    report.finished_at = now_iso()
    return report


def clean_worktree() -> tuple[bool, str]:
    code, output = git("status", "--porcelain")
    if code != 0:
        return False, output
    return output == "", output or "working tree clean"


def update(remote: str, branch: str, apply: bool) -> CaretakerReport:
    report = CaretakerReport(operation="update")
    clean, detail = clean_worktree()
    report.actions.append(asdict(Action("worktree_check", "repository", "healthy" if clean else "blocked", detail)))
    if not clean:
        report.status = "blocked"
        report.finished_at = now_iso()
        return report

    code, checkpoint = git("rev-parse", "HEAD")
    if code != 0:
        report.status = "failed"
        report.actions.append(asdict(Action("checkpoint", "HEAD", "failed", checkpoint)))
        report.finished_at = now_iso()
        return report
    report.checkpoint = checkpoint

    code, output = git("fetch", "--prune", remote, branch)
    report.actions.append(asdict(Action("fetch", f"{remote}/{branch}", "completed" if code == 0 else "failed", output or "fetch completed")))
    if code != 0:
        report.status = "failed"
        report.finished_at = now_iso()
        return report

    code, counts = git("rev-list", "--left-right", "--count", f"HEAD...{remote}/{branch}")
    if code != 0:
        report.status = "failed"
        report.actions.append(asdict(Action("compare", f"HEAD...{remote}/{branch}", "failed", counts)))
        report.finished_at = now_iso()
        return report

    report.actions.append(asdict(Action("compare", f"HEAD...{remote}/{branch}", "completed", counts)))
    if not apply:
        report.status = "update_available" if counts.split()[-1] != "0" else "current"
        report.finished_at = now_iso()
        return report

    code, output = git("merge", "--ff-only", f"{remote}/{branch}")
    report.actions.append(asdict(Action("fast_forward", f"{remote}/{branch}", "completed" if code == 0 else "failed", output)))
    if code != 0:
        report.status = "failed"
        report.finished_at = now_iso()
        return report

    healthy, validation_detail = validate()
    report.actions.append(asdict(Action("post_update_validation", "agent foundation", "healthy" if healthy else "failed", validation_detail)))
    if healthy:
        report.status = "updated"
    else:
        rollback_code, rollback_output = git("reset", "--hard", checkpoint)
        report.actions.append(asdict(Action("automatic_rollback", checkpoint, "completed" if rollback_code == 0 else "failed", rollback_output)))
        report.status = "rolled_back" if rollback_code == 0 else "degraded"

    report.finished_at = now_iso()
    return report


def send_email(subject: str, body: str) -> str:
    host = os.environ.get("LIOREAL_SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("LIOREAL_SMTP_PORT", "465"))
    username = os.environ.get("LIOREAL_SMTP_USER")
    password = os.environ.get("LIOREAL_SMTP_PASSWORD")
    recipient = os.environ.get("LIOREAL_EMAIL_TO")
    sender = os.environ.get("LIOREAL_EMAIL_FROM", username or "")

    missing = [name for name, value in {
        "LIOREAL_SMTP_USER": username,
        "LIOREAL_SMTP_PASSWORD": password,
        "LIOREAL_EMAIL_TO": recipient,
        "LIOREAL_EMAIL_FROM": sender,
    }.items() if not value]
    if missing:
        raise RuntimeError("Email transport is not configured: " + ", ".join(missing))

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content(body)

    attempts = 3
    for attempt in range(1, attempts + 1):
        try:
            with smtplib.SMTP_SSL(host, port, timeout=30) as smtp:
                smtp.login(username, password)
                smtp.send_message(message)
            return f"sent to {recipient}"
        except (OSError, smtplib.SMTPException) as exc:
            if attempt == attempts:
                raise RuntimeError(f"Email failed after {attempts} attempts: {exc}") from exc
            time.sleep(2 ** attempt)
    raise RuntimeError("Email failed")


def report_body(report: CaretakerReport, evidence: Path) -> str:
    lines = [
        f"Lioreal caretaker operation: {report.operation}",
        f"Status: {report.status}",
        f"Started: {report.started_at}",
        f"Finished: {report.finished_at}",
        f"Evidence: {evidence.relative_to(ROOT)}",
        "",
        "Actions:",
    ]
    for action in report.actions:
        lines.append(f"- {action['status']}: {action['kind']} [{action['target']}] {action['detail']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Lioreal bounded caretaker")
    sub = parser.add_subparsers(dest="operation", required=True)

    heal_parser = sub.add_parser("heal")
    heal_parser.add_argument("--email", choices=("never", "failure", "always"), default="failure")

    update_parser = sub.add_parser("update")
    update_parser.add_argument("--remote", default="origin")
    update_parser.add_argument("--branch", default="ark/manifest-v1")
    update_parser.add_argument("--apply", action="store_true", help="Apply a clean fast-forward update and roll back on failed validation.")
    update_parser.add_argument("--email", choices=("never", "failure", "always"), default="always")

    args = parser.parse_args()
    report = heal() if args.operation == "heal" else update(args.remote, args.branch, args.apply)
    evidence = record(report)

    should_email = args.email == "always" or (args.email == "failure" and report.status in {"failed", "degraded", "blocked", "rolled_back"})
    if should_email:
        try:
            report.notification = send_email(f"Lioreal caretaker: {report.status}", report_body(report, evidence))
        except RuntimeError as exc:
            report.notification = f"not sent: {exc}"
        evidence = record(report)

    print(json.dumps(asdict(report), indent=2, sort_keys=True))
    print(f"Evidence: {evidence.relative_to(ROOT)}")
    return 0 if report.status in {"completed", "current", "update_available", "updated"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
