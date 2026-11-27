from __future__ import annotations

# Standard library imports
import re
from pathlib import Path
from typing import ClassVar, List


class TestBackOfficeImage:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[3]
    APP: ClassVar[Path] = ROOT / "frontend" / "apps" / "back-office"
    DOCKERFILE: ClassVar[Path] = APP / "Dockerfile"
    NGINX_CONF: ClassVar[Path] = APP / "nginx.conf"
    ENCODING: ClassVar[str] = "utf-8"
    FROM_PATTERN: ClassVar[str] = r"^FROM\s"
    LOCK_FILE: ClassVar[str] = "pnpm-lock.yaml"
    WORKSPACE_FILE: ClassVar[str] = "pnpm-workspace.yaml"
    PACKAGE_JSON: ClassVar[str] = "frontend/apps/back-office/package.json"
    INSTALL: ClassVar[str] = "pnpm install --frozen-lockfile"
    BUILD_PATTERN: ClassVar[str] = r"pnpm\s+--filter\s+@swarm/back-office\b.*\bbuild\b"
    NGINX_BASE: ClassVar[str] = "nginxinc/nginx-unprivileged"
    COPY_FROM_BUILD: ClassVar[str] = "--from=build"
    DIST: ClassVar[str] = "frontend/apps/back-office/dist"
    HTML_ROOT: ClassVar[str] = "/usr/share/nginx/html"
    CONF_SOURCE: ClassVar[str] = "frontend/apps/back-office/nginx.conf"
    CONF_TARGET: ClassVar[str] = "/etc/nginx/conf.d/default.conf"
    LISTEN_PATTERN: ClassVar[str] = r"listen\s+(\[::\]:)?8080\b"
    FALLBACK_PATTERN: ClassVar[str] = r"try_files\s+.*/index\.html"
    EXPOSE_PATTERN: ClassVar[str] = r"^EXPOSE\s+8080\b"

    def _lines(self) -> List[str]:
        text = self.DOCKERFILE.read_text(encoding=self.ENCODING).replace("\\\n", " ")
        lines = [line.strip() for line in text.splitlines()]
        return [line for line in lines if line and not line.startswith("#")]

    def _final_index(self, lines: List[str]) -> int:
        starts = [i for i, line in enumerate(lines) if re.match(self.FROM_PATTERN, line, re.IGNORECASE)]
        return starts[-1]

    def _build_stage(self) -> List[str]:
        lines = self._lines()
        return lines[: self._final_index(lines)]

    def _final_stage(self) -> List[str]:
        lines = self._lines()
        return lines[self._final_index(lines) :]

    def test_the_dockerfile_exists(self) -> None:
        assert self.DOCKERFILE.is_file()

    def test_the_build_stage_copies_the_workspace_files_and_the_package_manifest(self) -> None:
        copies = " ".join(line for line in self._build_stage() if line.upper().startswith("COPY"))
        assert self.LOCK_FILE in copies
        assert self.WORKSPACE_FILE in copies
        assert self.PACKAGE_JSON in copies

    def test_the_build_stage_installs_with_a_frozen_lockfile(self) -> None:
        assert any(self.INSTALL in line for line in self._build_stage())

    def test_the_build_stage_builds_the_back_office_with_pnpm_filter(self) -> None:
        assert any(re.search(self.BUILD_PATTERN, line) for line in self._build_stage())

    def test_the_final_stage_is_based_on_unprivileged_nginx(self) -> None:
        assert self.NGINX_BASE in self._final_stage()[0]

    def test_the_final_stage_copies_the_built_files_into_the_html_root(self) -> None:
        copies = [line for line in self._final_stage() if line.upper().startswith("COPY")]
        assert any(self.COPY_FROM_BUILD in line and self.DIST in line and self.HTML_ROOT in line for line in copies)

    def test_the_final_stage_copies_the_nginx_configuration_as_the_default_site(self) -> None:
        copies = [line for line in self._final_stage() if line.upper().startswith("COPY")]
        assert any(
            self.COPY_FROM_BUILD in line and self.CONF_SOURCE in line and self.CONF_TARGET in line for line in copies
        )

    def test_nginx_listens_on_8080(self) -> None:
        assert re.search(self.LISTEN_PATTERN, self.NGINX_CONF.read_text(encoding=self.ENCODING))

    def test_nginx_falls_back_to_the_index_page(self) -> None:
        assert re.search(self.FALLBACK_PATTERN, self.NGINX_CONF.read_text(encoding=self.ENCODING))

    def test_the_final_stage_exposes_8080(self) -> None:
        assert any(re.match(self.EXPOSE_PATTERN, line, re.IGNORECASE) for line in self._final_stage())
