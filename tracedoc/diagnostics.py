from __future__ import annotations

import sqlite3
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class DoctorStatus(str, Enum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True)
class DoctorReport:
    status: DoctorStatus
    python_executable: str
    python_version: str
    sqlite_version: str
    fts5_available: bool
    data_dir: Path
    data_dir_status: str
    messages: tuple[str, ...]


def check_fts5() -> bool:
    try:
        with sqlite3.connect(":memory:") as connection:
            connection.execute("CREATE VIRTUAL TABLE fts_probe USING fts5(content)")
    except sqlite3.Error:
        return False
    return True


def ensure_data_dir(data_dir: Path) -> str:
    if data_dir.exists():
        if data_dir.is_dir():
            return "exists"
        raise NotADirectoryError(f"{data_dir} exists but is not a directory")
    data_dir.mkdir(parents=True)
    return "created"


def run_doctor(project_root: Path | None = None, data_dir: Path | None = None) -> DoctorReport:
    root = Path.cwd() if project_root is None else project_root
    runtime_data_dir = data_dir if data_dir is not None else root / "data"
    messages: list[str] = []
    status = DoctorStatus.OK

    python_version = ".".join(str(part) for part in sys.version_info[:3])
    if sys.version_info < (3, 11):
        status = DoctorStatus.FAIL
        messages.append("Python 3.11 or newer is required.")

    fts5_available = check_fts5()
    if not fts5_available:
        status = DoctorStatus.FAIL
        messages.append("SQLite FTS5 is not available.")

    try:
        data_dir_status = ensure_data_dir(runtime_data_dir)
    except OSError as exc:
        status = DoctorStatus.FAIL
        data_dir_status = "unavailable"
        messages.append(f"Data directory is not usable: {exc}")

    if status == DoctorStatus.OK:
        messages.append("Local runtime checks passed.")

    return DoctorReport(
        status=status,
        python_executable=sys.executable,
        python_version=python_version,
        sqlite_version=sqlite3.sqlite_version,
        fts5_available=fts5_available,
        data_dir=runtime_data_dir,
        data_dir_status=data_dir_status,
        messages=tuple(messages),
    )
