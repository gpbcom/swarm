from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_wheel(out_dir: Path) -> Path:
    maturin = Path(sys.executable).parent / "maturin"
    command = str(maturin) if maturin.exists() else shutil.which("maturin")
    assert command, "maturin was not found next to the interpreter or on the PATH."
    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
    target_dir = repo_root() / "packages" / "rust" / "target" / "wheel-tests" / worker
    manifest = repo_root() / "packages" / "rust" / "swarm-core" / "python" / "Cargo.toml"
    result = subprocess.run(
        [
            command,
            "build",
            "--release",
            "--manifest-path",
            str(manifest),
            "--target-dir",
            str(target_dir),
            "--interpreter",
            sys.executable,
            "--out",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"maturin failed:\n{result.stdout}\n{result.stderr}"
    wheels = list(out_dir.glob("*.whl"))
    assert len(wheels) == 1, f"Expected one wheel in {out_dir}, found {wheels}."
    return wheels[0]


def make_venv(folder: Path) -> Path:
    uv = shutil.which("uv")
    assert uv, "uv was not found on the PATH."
    result = subprocess.run(
        [uv, "venv", "--python", sys.executable, str(folder)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"uv venv failed:\n{result.stdout}\n{result.stderr}"
    return folder / "bin" / "python"


def install(python: Path, wheel: Path) -> None:
    uv = shutil.which("uv")
    assert uv, "uv was not found on the PATH."
    result = subprocess.run(
        [uv, "pip", "install", "--python", str(python), "--no-deps", str(wheel)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"uv pip install failed:\n{result.stdout}\n{result.stderr}"


def run_python(python: Path, code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(python), "-I", "-c", code], capture_output=True, text=True, check=False)
