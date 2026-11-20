from __future__ import annotations

from pathlib import Path
from typing import Optional

import pytest
from fastapi import FastAPI

from swarm_rest.api.cli.openapi_export_command import OpenApiExportCommand


class TestOpenApiExportCommand:
    ENCODING = "utf-8"
    TITLE = "Flotte de drones é"
    VERSION = "1.0.0"
    OTHER_CONTENT = "{}\n"
    EXIT_OK = 0
    EXIT_DIFFERENT = 1

    def an_app(self) -> FastAPI:
        return FastAPI(title=self.TITLE, version=self.VERSION)

    def test_writing_creates_the_folders_and_the_document(self, tmp_path: Path) -> None:
        path = tmp_path / "a" / "b" / "openapi.json"
        command = OpenApiExportCommand(self.an_app(), path, check=False)
        command.execute()
        assert command.exit_code == self.EXIT_OK
        assert path.read_text(encoding=self.ENCODING) == command.render()

    def test_the_document_is_indented_unescaped_and_ends_with_a_newline(self, tmp_path: Path) -> None:
        command = OpenApiExportCommand(self.an_app(), tmp_path / "openapi.json", check=False)
        rendered = command.render()
        assert rendered.endswith("\n")
        assert self.TITLE in rendered
        assert rendered.startswith("{\n  ")

    def test_checking_an_identical_file_succeeds_and_leaves_it_unchanged(self, tmp_path: Path) -> None:
        path = tmp_path / "openapi.json"
        OpenApiExportCommand(self.an_app(), path, check=False).execute()
        before = path.read_bytes()
        command = OpenApiExportCommand(self.an_app(), path, check=True)
        command.execute()
        assert command.exit_code == self.EXIT_OK
        assert path.read_bytes() == before

    @pytest.mark.parametrize("existing", [None, OTHER_CONTENT])
    def test_checking_a_different_or_missing_file_fails_and_writes_nothing(
        self, tmp_path: Path, existing: Optional[str]
    ) -> None:
        path = tmp_path / "openapi.json"
        if existing is not None:
            path.write_text(existing, encoding=self.ENCODING)
        command = OpenApiExportCommand(self.an_app(), path, check=True)
        command.execute()
        assert command.exit_code == self.EXIT_DIFFERENT
        if existing is None:
            assert not path.exists()
        else:
            assert path.read_text(encoding=self.ENCODING) == existing
