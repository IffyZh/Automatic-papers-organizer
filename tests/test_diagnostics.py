from __future__ import annotations

import subprocess
import sys

from tracedoc.diagnostics import DoctorReport, check_fts5, run_doctor


def test_run_doctor_returns_structured_result(tmp_path):
    report = run_doctor(project_root=tmp_path)

    assert isinstance(report, DoctorReport)
    assert report.python_version
    assert report.sqlite_version
    assert isinstance(report.fts5_available, bool)


def test_check_fts5_returns_actual_probe_result():
    assert isinstance(check_fts5(), bool)


def test_run_doctor_creates_temp_data_dir(tmp_path):
    data_dir = tmp_path / "runtime-data"

    report = run_doctor(data_dir=data_dir)

    assert data_dir.is_dir()
    assert report.data_dir == data_dir
    assert report.data_dir_status == "created"


def test_doctor_command_outputs_expected_sections():
    completed = subprocess.run(
        [sys.executable, "-m", "tracedoc", "doctor"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "TraceDoc" in completed.stdout
    assert "Python" in completed.stdout
    assert "SQLite" in completed.stdout
    assert "FTS5" in completed.stdout


def test_help_command_succeeds():
    completed = subprocess.run(
        [sys.executable, "-m", "tracedoc", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "doctor" in completed.stdout
