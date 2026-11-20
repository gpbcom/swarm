from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar, List


class TestPx4SitlImage:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    DOCKERFILE: ClassVar[Path] = ROOT / "deploy" / "images" / "px4-sitl" / "Dockerfile"
    VERSION_PATTERN: ClassVar[str] = r"^v\d+\.\d+\.\d+$"
    VERSION_ARG: ClassVar[str] = "PX4_VERSION"
    MODEL: ClassVar[str] = "gz_x500"
    MODEL_VARIABLE: ClassVar[str] = "PX4_SIM_MODEL"
    HEADLESS_VARIABLE: ClassVar[str] = "HEADLESS"
    TARGET: ClassVar[str] = "px4_sitl"
    REPOSITORY: ClassVar[str] = "PX4-Autopilot"
    MAVLINK_PORT: ClassVar[str] = "18570/udp"
    ROOT_USERS: ClassVar[List[str]] = ["root", "0"]

    def _lines(self) -> List[str]:
        assert self.DOCKERFILE.is_file()
        text = self.DOCKERFILE.read_text(encoding="utf-8").replace("\\\n", " ")
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _instructions(self, name: str) -> List[str]:
        pattern = re.compile(rf"^{name}\s+(.*)$", re.IGNORECASE)
        return [m.group(1) for m in map(pattern.match, self._lines()) if m]

    def _text(self) -> str:
        return "\n".join(self._lines())

    def test_the_dockerfile_exists(self) -> None:
        assert self.DOCKERFILE.is_file()

    def test_it_has_at_least_two_stages(self) -> None:
        assert len(self._instructions("FROM")) >= 2

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

    def test_the_px4_version_argument_is_pinned_to_a_release_tag(self) -> None:
        values = [
            arg.partition("=")[2].strip().strip("\"'")
            for arg in self._instructions("ARG")
            if arg.partition("=")[0].strip() == self.VERSION_ARG
        ]
        assert values
        assert re.match(self.VERSION_PATTERN, values[0])

    def test_the_version_is_used_to_check_out_px4_autopilot(self) -> None:
        text = self._text()
        assert self.REPOSITORY in text
        assert f"${self.VERSION_ARG}" in text or f"${{{self.VERSION_ARG}}}" in text

    def test_it_builds_the_px4_sitl_target(self) -> None:
        runs = [run for run in self._instructions("RUN") if self.TARGET in run]
        assert runs

    def test_it_runs_headless(self) -> None:
        env = " ".join(self._instructions("ENV"))
        assert re.search(rf"\b{self.HEADLESS_VARIABLE}[= ]\"?1\b", env)

    def test_it_selects_the_gazebo_x500_model(self) -> None:
        env = " ".join(self._instructions("ENV"))
        assert re.search(rf"\b{self.MODEL_VARIABLE}[= ]\"?{self.MODEL}\b", env)

    def test_it_exposes_the_mavlink_udp_port(self) -> None:
        ports = " ".join(self._instructions("EXPOSE")).split()
        assert self.MAVLINK_PORT in ports

    def test_the_last_user_is_not_root(self) -> None:
        users = self._instructions("USER")
        assert users
        assert users[-1].strip().lower() not in self.ROOT_USERS
