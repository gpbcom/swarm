from __future__ import annotations

# Standard library imports
import re
from pathlib import Path
from typing import ClassVar, List


class TestSimulatorImage:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    DOCKERFILE: ClassVar[Path] = ROOT / "services" / "simulator" / "Dockerfile"
    CARGO_BUILD: ClassVar[str] = "cargo build"
    CARGO_FLAGS: ClassVar[List[str]] = ["--release", "--locked", "-p swarm-synthetic-drones"]
    UV_SYNC: ClassVar[str] = "uv sync"
    UV_FLAGS: ClassVar[List[str]] = ["--frozen", "--no-dev", "--package swarm-simulator"]
    UV_FILES: ClassVar[List[str]] = ["uv.lock", "pyproject.toml"]
    BINARY: ClassVar[str] = "swarm-synthetic-drones"
    CONF: ClassVar[str] = "conf"
    ENTRYPOINT: ClassVar[str] = "swarm-simulator"
    RUST_DIRECTORY: ClassVar[str] = "rust"
    ROOT_USERS: ClassVar[List[str]] = ["root", "0"]

    def _lines(self) -> List[str]:
        assert self.DOCKERFILE.is_file()
        text = self.DOCKERFILE.read_text(encoding="utf-8").replace("\\\n", " ")
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _instructions(self, name: str) -> List[str]:
        pattern = re.compile(rf"^{name}\s+(.*)$", re.IGNORECASE)
        return [m.group(1) for m in map(pattern.match, self._lines()) if m]

    def _runs(self, command: str) -> List[str]:
        return [run for run in self._instructions("RUN") if command in run]

    def _text(self) -> str:
        return "\n".join(self._lines())

    def test_the_dockerfile_exists(self) -> None:
        assert self.DOCKERFILE.is_file()

    def test_it_has_at_least_three_stages(self) -> None:
        assert len(self._instructions("FROM")) >= 3

    def test_every_base_image_has_an_explicit_tag_that_is_not_latest(self) -> None:
        stages = self._instructions("FROM")
        assert stages
        names = {s.split()[-1] for s in stages if " AS " in s.upper()}
        for stage in stages:
            image = stage.split()[0]
            if image in names:
                continue
            _, separator, tag = image.rpartition(":")
            assert separator
            assert tag
            assert tag != "latest"

    def test_the_rust_stage_builds_the_synthetic_drones_in_release_mode(self) -> None:
        runs = self._runs(self.CARGO_BUILD)
        assert runs
        for flag in self.CARGO_FLAGS:
            assert flag in runs[0]

    def test_the_cargo_build_runs_from_the_rust_workspace(self) -> None:
        assert self.RUST_DIRECTORY in self._text()

    def test_the_python_stage_syncs_the_frozen_runtime_dependencies(self) -> None:
        runs = self._runs(self.UV_SYNC)
        assert runs
        for flag in self.UV_FLAGS:
            assert flag in runs[0]

    def test_the_lock_and_the_project_files_are_copied_before_the_sync(self) -> None:
        lines = self._lines()
        sync = next(i for i, line in enumerate(lines) if self.UV_SYNC in line)
        copied = "\n".join(line for line in lines[:sync] if line.upper().startswith("COPY"))
        for name in self.UV_FILES:
            assert name in copied

    def test_the_runtime_stage_copies_the_binary_and_the_conf(self) -> None:
        last_stage = self._text().upper().rsplit("\nFROM ", 1)[-1]
        assert self.BINARY.upper() in last_stage
        assert f"{self.CONF}/".upper() in last_stage

    def test_the_last_user_is_not_root(self) -> None:
        users = self._instructions("USER")
        assert users
        assert users[-1].strip().lower() not in self.ROOT_USERS

    def test_the_entrypoint_runs_the_simulator(self) -> None:
        entrypoints = self._instructions("ENTRYPOINT")
        assert entrypoints
        assert self.ENTRYPOINT in entrypoints[-1]
