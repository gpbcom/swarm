from __future__ import annotations

# Standard library imports
import re
from pathlib import Path
from typing import ClassVar, List, Optional, Tuple

# Third-party imports
import pytest


class TestServiceImages:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    SERVICES: ClassVar[List[Path]] = sorted(
        path
        for path in (Path(__file__).resolve().parents[3] / "services").iterdir()
        if path.is_dir() and not path.name.startswith((".", "_"))
    )
    DOCKERFILES: ClassVar[List[Path]] = sorted(
        [*(Path(__file__).resolve().parents[3] / "services").glob("*/Dockerfile")]
        + [*(Path(__file__).resolve().parents[3] / "backend" / "apps").glob("*/Dockerfile")]
        + [*(Path(__file__).resolve().parents[3] / "frontends").glob("*/Dockerfile")]
    )
    SERVICE_DOCKERFILES: ClassVar[List[Path]] = sorted(
        (Path(__file__).resolve().parents[3] / "services").glob("*/Dockerfile")
    )
    APPS: ClassVar[List[Path]] = sorted(
        path for path in (Path(__file__).resolve().parents[3] / "backend" / "apps").iterdir() if path.is_dir()
    )
    APP_DOCKERFILES: ClassVar[List[Path]] = sorted(
        (Path(__file__).resolve().parents[3] / "backend" / "apps").glob("*/Dockerfile")
    )
    APP_KEY: ClassVar[str] = "SWARM_APP"
    APP_ROOT_KEY: ClassVar[str] = "SWARM_APP_ROOT"
    APP_LAYERS: ClassVar[List[str]] = [
        "backend/swarm-models",
        "backend/swarm-storage",
        "backend/swarm-clients",
        "backend/swarm-service",
        "backend/swarm-api",
    ]
    MIGRATIONS_SCRIPT: ClassVar[str] = "--package swarm-scripts"
    ENV: ClassVar[str] = "ENV"
    HOME_KEY: ClassVar[str] = "SWARM_{service}_HOME"
    COPY_FROM_BUILD: ClassVar[str] = "--from=build"
    CONF_SUFFIX: ClassVar[str] = "/conf"
    DOCKERIGNORE: ClassVar[Path] = ROOT / ".dockerignore"
    GATEWAY: ClassVar[Path] = ROOT / "backend" / "apps" / "gateway" / "Dockerfile"
    GATEWAY_COMMAND: ClassVar[str] = "swarm-gateway-serve"
    LOCK_FILE: ClassVar[str] = "uv.lock"
    FROM: ClassVar[str] = "FROM"
    USER: ClassVar[str] = "USER"
    COPY: ClassVar[str] = "COPY"
    ENTRYPOINT: ClassVar[str] = "ENTRYPOINT"
    CMD: ClassVar[str] = "CMD"
    LATEST: ClassVar[str] = "latest"
    ROOT_USERS: ClassVar[Tuple[str, ...]] = ("root", "0")
    IGNORED: ClassVar[Tuple[str, ...]] = (".git", "node_modules", ".venv", "target", ".env")

    def _lines(self, dockerfile: Path) -> List[str]:
        text = dockerfile.read_text(encoding="utf-8").replace("\\\n", " ")
        lines = [line.strip() for line in text.splitlines()]
        return [line for line in lines if line and not line.startswith("#")]

    def _instructions(self, lines: List[str], name: str) -> List[str]:
        pattern = re.compile(rf"^{name}\s+(.*)$", re.IGNORECASE)
        return [m.group(1) for m in map(pattern.match, lines) if m]

    def _final_stage(self, dockerfile: Path) -> List[str]:
        lines = self._lines(dockerfile)
        starts = [i for i, line in enumerate(lines) if re.match(rf"^{self.FROM}\s", line, re.IGNORECASE)]
        return lines[starts[-1] :]

    def _copy_sources(self, dockerfile: Path) -> List[str]:
        sources: List[str] = []
        for arguments in self._instructions(self._lines(dockerfile), self.COPY):
            words = [word for word in arguments.split() if not word.startswith("--")]
            sources.extend(words[:-1])
        return sources

    def _env_entries(self, dockerfile: Path) -> List[Tuple[str, str]]:
        entries: List[Tuple[str, str]] = []
        for arguments in self._instructions(self._final_stage(dockerfile), self.ENV):
            entries.extend(re.findall(r"(\w+)=(\S+)", arguments))
        return entries

    def _conf_destination(self, dockerfile: Path) -> Optional[str]:
        for arguments in self._instructions(self._final_stage(dockerfile), self.COPY):
            words = [word for word in arguments.split() if not word.startswith("--")]
            if self.COPY_FROM_BUILD in arguments and words[0].endswith(self.CONF_SUFFIX):
                return words[-1][: -len(self.CONF_SUFFIX)]
        return None

    @pytest.mark.parametrize("dockerfile", SERVICE_DOCKERFILES, ids=lambda path: str(path.parent.name))
    def test_the_runtime_stage_names_the_folder_its_conf_is_copied_to(self, dockerfile: Path) -> None:
        destination = self._conf_destination(dockerfile)
        if destination is None:
            pytest.skip("This image does not copy its conf folder from the build stage.")
        key = self.HOME_KEY.format(service=dockerfile.parent.name.upper().replace("-", "_"))
        assert (key, destination) in self._env_entries(dockerfile)

    @pytest.mark.parametrize("dockerfile", APP_DOCKERFILES, ids=lambda path: str(path.parent.name))
    def test_an_app_image_names_its_app_and_the_folder_its_conf_is_copied_to(self, dockerfile: Path) -> None:
        destination = self._conf_destination(dockerfile)
        entries = self._env_entries(dockerfile)
        assert destination is not None
        assert (self.APP_ROOT_KEY, destination) in entries
        assert (self.APP_KEY, dockerfile.parent.name) in entries

    @pytest.mark.parametrize("app", APPS, ids=lambda path: path.name)
    def test_every_app_has_a_dockerfile(self, app: Path) -> None:
        assert (app / "Dockerfile").is_file()

    @pytest.mark.parametrize("dockerfile", APP_DOCKERFILES, ids=lambda path: str(path.parent.name))
    def test_an_app_image_builds_from_the_root_with_its_layers_and_the_migrations_script(
        self, dockerfile: Path
    ) -> None:
        sources = self._copy_sources(dockerfile)
        text = dockerfile.read_text(encoding="utf-8")
        assert self.LOCK_FILE in sources
        assert f"backend/apps/{dockerfile.parent.name}/pyproject.toml" in sources
        assert all(f"{layer}/pyproject.toml" in sources for layer in self.APP_LAYERS)
        assert self.MIGRATIONS_SCRIPT in text

    @pytest.mark.parametrize("service", SERVICES, ids=lambda path: path.name)
    def test_every_service_has_a_dockerfile(self, service: Path) -> None:
        assert (service / "Dockerfile").is_file()

    @pytest.mark.parametrize("dockerfile", DOCKERFILES, ids=lambda path: str(path.parent.name))
    def test_the_dockerfile_is_multi_stage(self, dockerfile: Path) -> None:
        assert len(self._instructions(self._lines(dockerfile), self.FROM)) >= 2

    @pytest.mark.parametrize("dockerfile", DOCKERFILES, ids=lambda path: str(path.parent.name))
    def test_every_external_base_is_pinned(self, dockerfile: Path) -> None:
        stages: List[str] = []
        for arguments in self._instructions(self._lines(dockerfile), self.FROM):
            words = [word for word in arguments.split() if not word.startswith("--")]
            base = words[0]
            if base not in stages:
                _, _, tag = base.partition(":")
                assert "@sha256:" in base or (tag and tag != self.LATEST), base
            if len(words) >= 3:
                stages.append(words[2])

    @pytest.mark.parametrize("dockerfile", DOCKERFILES, ids=lambda path: str(path.parent.name))
    def test_the_final_stage_runs_as_a_non_root_user(self, dockerfile: Path) -> None:
        users = self._instructions(self._final_stage(dockerfile), self.USER)
        assert users
        assert users[-1].strip().split(":")[0] not in self.ROOT_USERS

    @pytest.mark.parametrize("dockerfile", DOCKERFILES, ids=lambda path: str(path.parent.name))
    def test_the_final_stage_has_an_entrypoint_or_a_command(self, dockerfile: Path) -> None:
        stage = self._final_stage(dockerfile)
        assert self._instructions(stage, self.ENTRYPOINT) or self._instructions(stage, self.CMD)

    @pytest.mark.parametrize("dockerfile", DOCKERFILES, ids=lambda path: str(path.parent.name))
    def test_the_build_context_is_the_repository_root(self, dockerfile: Path) -> None:
        if dockerfile.parents[1].name != self.ROOT.joinpath("services").name:
            pytest.skip("Only service Dockerfiles are checked.")
        sources = self._copy_sources(dockerfile)
        assert self.LOCK_FILE in sources
        assert any(source.startswith(f"services/{dockerfile.parent.name}") for source in sources)

    def test_the_gateway_runs_swarm_gateway(self) -> None:
        stage = self._final_stage(self.GATEWAY)
        commands = self._instructions(stage, self.ENTRYPOINT) + self._instructions(stage, self.CMD)
        assert any(self.GATEWAY_COMMAND in command for command in commands)

    @pytest.mark.parametrize("pattern", IGNORED)
    def test_the_root_dockerignore_excludes(self, pattern: str) -> None:
        lines = self.DOCKERIGNORE.read_text(encoding="utf-8").splitlines()
        assert any(pattern in line for line in lines if not line.strip().startswith("#"))
