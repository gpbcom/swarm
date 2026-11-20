from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar, List


class TestPostgresImage:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    DOCKERFILE: ClassVar[Path] = ROOT / "deploy" / "images" / "postgres" / "Dockerfile"
    BASE_REPOSITORY: ClassVar[str] = "ghcr.io/cloudnative-pg/postgis"
    TIMESCALE_PACKAGE: ClassVar[str] = "timescaledb-2-postgresql-16"
    POSTGRES_USER: ClassVar[str] = "26"

    def _lines(self) -> List[str]:
        text = self.DOCKERFILE.read_text(encoding="utf-8")
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _instructions(self, name: str) -> List[str]:
        pattern = re.compile(rf"^{name}\s+(.*)$", re.IGNORECASE)
        return [m.group(1) for m in map(pattern.match, self._lines()) if m]

    def test_the_dockerfile_exists(self) -> None:
        assert self.DOCKERFILE.is_file()

    def test_the_base_is_cloudnative_pg_postgis_16(self) -> None:
        base = self._instructions("FROM")[0].split()[0]
        repository, _, tag = base.partition(":")
        assert repository == self.BASE_REPOSITORY
        assert tag.startswith("16")
        assert tag != "latest"

    def test_it_installs_the_timescaledb_package(self) -> None:
        assert self.TIMESCALE_PACKAGE in "\n".join(self._lines())

    def test_the_last_user_is_the_cloudnative_pg_postgres_user(self) -> None:
        assert self._instructions("USER")[-1].strip() == self.POSTGRES_USER
