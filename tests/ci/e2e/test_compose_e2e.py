from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar, Dict, List, cast

import yaml
from pydantic import JsonValue


class TestComposeE2e:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    COMPOSE: ClassVar[str] = "compose.e2e.yaml"
    ENCODING: ClassVar[str] = "utf-8"
    SERVICES_KEY: ClassVar[str] = "services"
    BUILD_KEY: ClassVar[str] = "build"
    IMAGE_KEY: ClassVar[str] = "image"
    VOLUMES_KEY: ClassVar[str] = "volumes"
    SOURCE_KEY: ClassVar[str] = "source"
    COMMAND_KEY: ClassVar[str] = "command"
    ENTRYPOINT_KEY: ClassVar[str] = "entrypoint"
    GATEWAY: ClassVar[str] = "gateway"
    DOCKERFILE: ClassVar[str] = "Dockerfile"
    SERVICES_FOLDER: ClassVar[str] = "services"
    FRONTENDS_FOLDER: ClassVar[str] = "frontends"
    SOURCE_FOLDERS: ClassVar[List[str]] = ["services", "frontends", "packages"]
    IMAGE_PATTERN: ClassVar[str] = (
        r"^\$\{SWARM_IMAGE_REGISTRY:-ghcr\.io/gpbcom/swarm\}/%s:\$\{SWARM_IMAGE_TAG:\?[^}]+\}$"
    )
    DEV_SERVER_WORDS: ClassVar[List[str]] = ["--reload", "vite", "pnpm dev", "npm run dev", "uvicorn --reload"]

    def services(self) -> Dict[str, Dict[str, JsonValue]]:
        text = (self.ROOT / self.COMPOSE).read_text(encoding=self.ENCODING)
        data = cast(Dict[str, JsonValue], yaml.safe_load(text))
        return cast(Dict[str, Dict[str, JsonValue]], data[self.SERVICES_KEY])

    def volume_sources(self, service: Dict[str, JsonValue]) -> List[str]:
        sources: List[str] = []
        for volume in cast(List[JsonValue], service.get(self.VOLUMES_KEY) or []):
            if isinstance(volume, str):
                sources.append(volume.split(":")[0])
            else:
                sources.append(str(cast(Dict[str, JsonValue], volume).get(self.SOURCE_KEY, "")))
        return sources

    def commands(self, service: Dict[str, JsonValue]) -> str:
        parts = [service.get(self.COMMAND_KEY), service.get(self.ENTRYPOINT_KEY)]
        return " ".join(" ".join(part) if isinstance(part, list) else str(part or "") for part in parts)

    def test_the_file_declares_services_including_the_gateway(self) -> None:
        services = self.services()
        assert services
        assert self.GATEWAY in services

    def test_no_service_is_built(self) -> None:
        for name, service in self.services().items():
            assert self.BUILD_KEY not in service, name

    def test_every_service_uses_the_published_image_of_its_own_name(self) -> None:
        for name, service in self.services().items():
            image = str(service.get(self.IMAGE_KEY, ""))
            assert re.match(self.IMAGE_PATTERN % re.escape(name), image), name

    def test_every_image_name_is_a_service_or_front_end_with_a_dockerfile(self) -> None:
        for name in self.services():
            folders = [self.ROOT / self.SERVICES_FOLDER / name, self.ROOT / self.FRONTENDS_FOLDER / name]
            assert any((folder / self.DOCKERFILE).is_file() for folder in folders), name

    def test_no_service_mounts_source_code(self) -> None:
        for name, service in self.services().items():
            for source in self.volume_sources(service):
                assert not source.startswith("."), (name, source)
                for folder in self.SOURCE_FOLDERS:
                    assert not source.startswith(str(self.ROOT / folder)), (name, source)
                assert Path(source) != self.ROOT, (name, source)

    def test_no_service_runs_a_development_server(self) -> None:
        for name, service in self.services().items():
            command = self.commands(service)
            for word in self.DEV_SERVER_WORDS:
                assert word not in command, (name, word)
