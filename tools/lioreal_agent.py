#!/usr/bin/env python3
"""Lioreal's local-first repository caretaker.

The agent performs deterministic, network-free inspection and writes a Markdown
health report. It is intentionally modest: repair proposals belong in reviewed
pull requests, while observation may run unattended.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "field-notes" / "agent" / "latest.md"
IGNORED_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__"}
TEXT_SUFFIXES = {
    ".md", ".txt", ".py", ".json", ".yaml", ".yml", ".toml", ".js", ".ts",
    ".tsx", ".jsx", ".html", ".css", ".scss", ".sh", ".sql",
}


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    message: str
    path: str | None = None


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        yield path


def git_output(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
        )
    except OSError:
        return "unavailable"
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def inspect() -> tuple[dict[str, object], list[Finding]]:
    files = sorted(iter_files(ROOT))
    relative = [path.relative_to(ROOT) for path in files]
    findings: list[Finding] = []

    required = {
        "README.md": "workshop entrance",
        "AGENTS.md": "agent charter",
        ".github/workflows/lioreal-agent.yml": "automation workflow",
    }
    for name, purpose in required.items():
        if not (ROOT / name).exists():
            findings.append(Finding("error", "missing-required", f"Missing {purpose}.", name))

    expected_rooms = [
        "garden", "laboratory", "architectures", "tools", "field-notes", "artifacts", "archive"
    ]
    missing_rooms = [room for room in expected_rooms if not (ROOT / room).exists()]
    if missing_rooms:
        findings.append(
            Finding(
                "notice",
                "rooms-not-yet-formed",
                "README rooms not yet present: " + ", ".join(missing_rooms),
            )
        )

    markers = ("TODO", "FIXME", "XXX", "HACK")
    marker_hits: list[str] = []
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES or path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if any(marker in line for marker in markers):
                marker_hits.append(f"{path.relative_to(ROOT)}:{line_no}")
    if marker_hits:
        findings.append(
            Finding(
                "notice",
                "open-markers",
                f"Found {len(marker_hits)} open work marker(s): " + ", ".join(marker_hits[:12]),
            )
        )

    summary: dict[str, object] = {
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "branch": git_output("branch", "--show-current"),
        "commit": git_output("rev-parse", "--short", "HEAD"),
        "tracked_files": len(relative),
        "top_level_entries": sorted(
            child.name for child in ROOT.iterdir() if child.name != ".git"
        ),
        "finding_counts": {
            level: sum(1 for finding in findings if finding.level == level)
            for level in ("error", "warning", "notice")
        },
    }
    return summary, findings


def render(summary: dict[str, object], findings: list[Finding]) -> str:
    counts = summary["finding_counts"]
    lines = [
        "# Lioreal Agent Report",
        "",
        f"Generated: `{summary['generated_at_utc']}`",
        f"Branch: `{summary['branch']}`",
        f"Commit: `{summary['commit']}`",
        f"Files observed: **{summary['tracked_files']}**",
        "",
        "## Signal",
        "",
        f"- Errors: **{counts['error']}**",
        f"- Warnings: **{counts['warning']}**",
        f"- Notices: **{counts['notice']}**",
        "",
        "## Findings",
        "",
    ]
    if not findings:
        lines.append("No actionable findings. The workshop is quiet, not dead.")
    else:
        for finding in findings:
            location = f" (`{finding.path}`)" if finding.path else ""
            lines.append(f"- **{finding.level.upper()} · {finding.code}**{location}: {finding.message}")

    lines.extend([
        "",
        "## Inventory",
        "",
        *[f"- `{entry}`" for entry in summary["top_level_entries"]],
        "",
        "## Machine-readable summary",
        "",
        "```json",
        json.dumps(summary, indent=2, sort_keys=True),
        "```",
        "",
        "_Generated by `tools/lioreal_agent.py`. Observation is autonomous; adoption remains reviewable._",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Return a non-zero exit code when error-level findings exist.",
    )
    args = parser.parse_args()

    summary, findings = inspect()
    report = args.report if args.report.is_absolute() else ROOT / args.report
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render(summary, findings), encoding="utf-8")
    print(f"Lioreal report written to {report.relative_to(ROOT)}")

    if args.fail_on_error and any(item.level == "error" for item in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
