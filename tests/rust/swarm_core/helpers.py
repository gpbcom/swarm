from __future__ import annotations

# Standard library imports
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

CRC_EXTRA_BY_MESSAGE_ID = {0: 50, 1: 124, 33: 104}
MAVLINK_2_MAGIC = 0xFD


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_wheel(out_dir: Path) -> Path:
    maturin = Path(sys.executable).parent / "maturin"
    command = str(maturin) if maturin.exists() else shutil.which("maturin")
    assert command, "maturin was not found next to the interpreter or on the PATH."
    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
    target_dir = repo_root() / "rust" / "target" / "wheel-tests" / worker
    manifest = repo_root() / "rust" / "swarm-core" / "python" / "Cargo.toml"
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


def mavlink_crc(data: bytes, crc_extra: int) -> int:
    crc = 0xFFFF
    for byte in data + bytes([crc_extra]):
        tmp = byte ^ (crc & 0xFF)
        tmp = (tmp ^ (tmp << 4)) & 0xFF
        crc = ((crc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)) & 0xFFFF
    return crc


def mavlink_frame(system_id: int, sequence: int, message_id: int, payload: bytes, component_id: int = 1) -> bytes:
    trimmed = payload.rstrip(b"\x00") or payload[:1]
    header = bytes([len(trimmed), 0, 0, sequence, system_id, component_id]) + message_id.to_bytes(3, "little")
    body = header + trimmed
    crc = mavlink_crc(body, CRC_EXTRA_BY_MESSAGE_ID[message_id])
    return bytes([MAVLINK_2_MAGIC]) + body + struct.pack("<H", crc)


def heartbeat_payload(base_mode: int, system_status: int) -> bytes:
    return struct.pack("<IBBBBB", 0, 2, 12, base_mode, system_status, 3)


def sys_status_payload(battery_remaining: int) -> bytes:
    return bytes(30) + struct.pack("<b", battery_remaining)


def global_position_int_payload(
    lat_e7: int,
    lon_e7: int,
    relative_alt_mm: int,
    vx_cm_s: int,
    vy_cm_s: int,
    hdg_cdeg: int,
    time_boot_ms: int = 0,
    alt_mm: int = 0,
    vz_cm_s: int = 0,
) -> bytes:
    return struct.pack(
        "<IiiiihhhH", time_boot_ms, lat_e7, lon_e7, alt_mm, relative_alt_mm, vx_cm_s, vy_cm_s, vz_cm_s, hdg_cdeg
    )
