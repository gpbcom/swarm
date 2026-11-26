from __future__ import annotations

# Standard library imports
import zipfile
from pathlib import Path
from typing import ClassVar, Tuple

# Third-party imports
import pytest

# First-party imports
from tests.rust.swarm_core.helpers import (
    build_wheel,
    global_position_int_payload,
    heartbeat_payload,
    install,
    make_venv,
    mavlink_frame,
    run_python,
    sys_status_payload,
)


class TestSwarmCoreWheel:
    FUNCTIONS: ClassVar[Tuple[str, ...]] = ("safety_tick", "planner_plan", "mavlink_encode")

    @pytest.fixture(scope="class")
    def built(self, tmp_path_factory: pytest.TempPathFactory) -> Tuple[Path, Path]:
        wheel = build_wheel(tmp_path_factory.mktemp("wheel"))
        python = make_venv(tmp_path_factory.mktemp("env") / "venv")
        install(python, wheel)
        return wheel, python

    def test_maturin_builds_exactly_one_wheel_named_after_the_module(self, built: Tuple[Path, Path]) -> None:
        wheel, _ = built
        assert wheel.name.startswith("swarm_core-")
        assert wheel.name.endswith(".whl")

    def test_the_wheel_holds_a_type_stub_for_the_module(self, built: Tuple[Path, Path]) -> None:
        wheel, _ = built
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
        assert any(name.startswith("swarm_core") and name.endswith(".pyi") for name in names)

    def test_the_module_comes_from_the_installed_wheel(self, built: Tuple[Path, Path]) -> None:
        _, python = built
        result = run_python(python, "import swarm_core; print(swarm_core.__file__)")
        assert result.returncode == 0, result.stderr
        assert Path(result.stdout.strip()).resolve().is_relative_to(python.parent.parent.resolve())

    @pytest.mark.parametrize("function", FUNCTIONS)
    @pytest.mark.parametrize(("values", "expected"), [("[1, 2, 3]", "6"), ("[]", "0")])
    def test_a_function_returns_the_wrapping_sum(
        self, built: Tuple[Path, Path], function: str, values: str, expected: str
    ) -> None:
        _, python = built
        result = run_python(python, f"import swarm_core; print(swarm_core.{function}({values}))")
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == expected

    @pytest.mark.parametrize("function", FUNCTIONS)
    def test_a_non_integer_value_raises_a_type_error(self, built: Tuple[Path, Path], function: str) -> None:
        _, python = built
        code = (
            "import swarm_core\n"
            "try:\n"
            f"    swarm_core.{function}(['a'])\n"
            "except Exception as error:\n"
            "    print(type(error).__name__)\n"
        )
        result = run_python(python, code)
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "TypeError"

    def _frames(self) -> Tuple[bytes, bytes, bytes]:
        heartbeat = mavlink_frame(7, 0, 0, heartbeat_payload(base_mode=129, system_status=4))
        status = mavlink_frame(7, 1, 1, sys_status_payload(87))
        position = mavlink_frame(
            7, 2, 33, global_position_int_payload(473977420, 85455940, 12500, 300, -400, 9000, time_boot_ms=1000)
        )
        return heartbeat, status, position

    def test_latest_frames_ingests_frames_into_one_drone_sample(self, built: Tuple[Path, Path]) -> None:
        _, python = built
        heartbeat, status, position = self._frames()
        code = (
            "import swarm_core\n"
            "latest = swarm_core.LatestFrames()\n"
            f"counts = [latest.ingest(bytes.fromhex(h), 5000) for h in ['{heartbeat.hex()}', '{status.hex()}',"
            f" '{position.hex()}']]\n"
            "samples = latest.snapshot()\n"
            "sample = samples[0]\n"
            "print(counts, len(samples))\n"
            "print(sample.system_id, sample.has_position, sample.lat_e7, sample.lon_e7, sample.relative_alt_mm,"
            " sample.hdg_cdeg, sample.battery_remaining, sample.system_status, sample.received, sample.lost,"
            " sample.updated_at_us)\n"
        )
        result = run_python(python, code)
        assert result.returncode == 0, result.stderr
        counts_line, sample_line = result.stdout.strip().splitlines()
        assert counts_line == "[1, 1, 1] 1"
        assert sample_line == "7 True 473977420 85455940 12500 9000 87 4 3 0 5000"

    def test_a_frame_with_a_corrupted_crc_is_not_ingested(self, built: Tuple[Path, Path]) -> None:
        _, python = built
        frame = bytearray(self._frames()[2])
        frame[-1] ^= 0xFF
        code = (
            "import swarm_core\n"
            "latest = swarm_core.LatestFrames()\n"
            f"print(latest.ingest(bytes.fromhex('{bytes(frame).hex()}'), 5000), len(latest.snapshot()))\n"
        )
        result = run_python(python, code)
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "0 0"

    def test_a_non_bytes_datagram_raises_a_type_error(self, built: Tuple[Path, Path]) -> None:
        _, python = built
        code = (
            "import swarm_core\n"
            "try:\n"
            "    swarm_core.LatestFrames().ingest('text', 1)\n"
            "except Exception as error:\n"
            "    print(type(error).__name__)\n"
        )
        result = run_python(python, code)
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "TypeError"
