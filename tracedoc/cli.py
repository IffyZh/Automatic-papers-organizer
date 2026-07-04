from __future__ import annotations

import argparse
from pathlib import Path

from tracedoc.diagnostics import DoctorStatus, run_doctor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tracedoc",
        description="TraceDoc command line tools.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "doctor",
        help="Check the local TraceDoc runtime environment.",
    )
    return parser


def format_doctor_report(project_root: Path) -> tuple[str, int]:
    report = run_doctor(project_root=project_root)
    lines = [
        "TraceDoc doctor",
        f"Status: {report.status.value.upper()}",
        f"Python: {report.python_version} ({report.python_executable})",
        f"SQLite: {report.sqlite_version}",
        f"FTS5: {'available' if report.fts5_available else 'unavailable'}",
        f"Data directory: {report.data_dir} ({report.data_dir_status})",
    ]
    if report.messages:
        lines.append("Messages:")
        lines.extend(f"- {message}" for message in report.messages)
    exit_code = 0 if report.status != DoctorStatus.FAIL else 1
    return "\n".join(lines), exit_code


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        output, exit_code = format_doctor_report(project_root=Path.cwd())
        print(output)
        return exit_code

    parser.print_help()
    return 0
