from __future__ import annotations

# Standard library imports
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def script_path() -> Path:
    return repo_root() / ".github" / "scripts" / "bench_gate.py"


def estimate(point: float) -> Dict[str, object]:
    return {
        "confidence_interval": {
            "confidence_level": 0.95,
            "lower_bound": point - 0.01,
            "upper_bound": point + 0.01,
        },
        "point_estimate": point,
        "standard_error": 0.005,
    }


def write_change(root: Path, bench_id: str, mean: float) -> None:
    for folder in ("change", "new"):
        path = root / bench_id / folder / "estimates.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"mean": estimate(mean), "median": estimate(mean)}), encoding="utf-8")


def run_gate(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script_path()), *args],
        capture_output=True,
        text=True,
        check=False,
    )
