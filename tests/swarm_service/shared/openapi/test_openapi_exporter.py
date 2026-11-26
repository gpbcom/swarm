from __future__ import annotations

# Standard library imports
import json
from pathlib import Path
from typing import ClassVar, Optional

# Third-party imports
import pytest
from fastapi import FastAPI

# First-party imports
from swarm_service.shared.openapi.openapi_exporter import OpenApiExporter


class TestOpenApiExporter:
    ENCODING: ClassVar[str] = "utf-8"
    TITLE: ClassVar[str] = "Flotte de drones é"
    VERSION: ClassVar[str] = "1.0.0"
    NAME: ClassVar[str] = "fleet"
    FILE_NAME: ClassVar[str] = "fleet.json"
    OTHER_CONTENT: ClassVar[str] = "{}\n"

    def an_exporter(self, root: Path) -> OpenApiExporter:
        return OpenApiExporter(FastAPI(title=self.TITLE, version=self.VERSION), root, self.NAME)

    def test_the_document_is_named_after_the_app(self, tmp_path: Path) -> None:
        exporter = self.an_exporter(tmp_path)

        assert exporter.file_name == self.FILE_NAME
        assert exporter.path == tmp_path / self.FILE_NAME

    def test_exporting_creates_the_folders_and_the_document(self, tmp_path: Path) -> None:
        root = tmp_path / "a" / "b"
        exporter = self.an_exporter(root)

        path = exporter.export()

        assert path == root / self.FILE_NAME
        assert path.read_text(encoding=self.ENCODING) == exporter.render()

    def test_the_document_is_indented_sorted_unescaped_and_ends_with_a_newline(self, tmp_path: Path) -> None:
        rendered = self.an_exporter(tmp_path).render()

        assert rendered.endswith("\n")
        assert self.TITLE in rendered
        assert rendered.startswith("{\n  ")
        assert rendered == json.dumps(json.loads(rendered), indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    def test_an_exported_document_is_not_stale_and_checking_leaves_it_unchanged(self, tmp_path: Path) -> None:
        exporter = self.an_exporter(tmp_path)
        before = exporter.export().read_bytes()

        assert exporter.is_stale() is False
        assert exporter.path.read_bytes() == before

    @pytest.mark.parametrize("existing", [None, OTHER_CONTENT])
    def test_a_different_or_missing_document_is_stale_and_checking_writes_nothing(
        self, tmp_path: Path, existing: Optional[str]
    ) -> None:
        exporter = self.an_exporter(tmp_path)
        if existing is not None:
            exporter.path.write_text(existing, encoding=self.ENCODING)

        assert exporter.is_stale() is True
        if existing is None:
            assert not exporter.path.exists()
        else:
            assert exporter.path.read_text(encoding=self.ENCODING) == existing
