from __future__ import annotations

import logging
from pathlib import Path

import pytest

from swarm_models.models.schemas.exceptions import SESchemaError, SESchemaUnreadableError, SESchemaUnwritableError
from swarm_models.storage.schemas.schema_folder import SchemaFolder


class TestSchemaFolder:
    def test_the_default_root_is_the_schemas_folder_of_swarm_models(self) -> None:
        assert SchemaFolder.DEFAULT_ROOT.is_absolute()
        assert SchemaFolder.DEFAULT_ROOT.parts[-2:] == ("swarm-models", "schemas")

    def test_the_attributes_hold_the_root_and_a_logger(self, tmp_path: Path) -> None:
        folder = SchemaFolder(tmp_path)
        assert folder.root == tmp_path
        assert isinstance(folder.logger, logging.Logger)

    def test_a_given_logger_is_used(self, tmp_path: Path) -> None:
        logger = logging.getLogger("tests.schema_folder.given")
        assert SchemaFolder(tmp_path, logger).logger is logger

    def test_the_path_of_a_name_is_under_the_root(self, tmp_path: Path) -> None:
        assert SchemaFolder(tmp_path).path("a.json") == tmp_path / "a.json"

    def test_reading_a_missing_file_gives_none(self, tmp_path: Path) -> None:
        assert SchemaFolder(tmp_path).read("missing.json") is None

    def test_a_write_then_read_round_trip_keeps_non_ascii_text(self, tmp_path: Path) -> None:
        folder = SchemaFolder(tmp_path)
        text = '{"titre": "Essaim de drones, été"}\n'
        folder.write("a.json", text)
        assert folder.read("a.json") == text

    def test_a_write_creates_a_missing_nested_root_and_returns_the_path(self, tmp_path: Path) -> None:
        folder = SchemaFolder(tmp_path / "one" / "two")
        path = folder.write("a.json", "{}")
        assert path == tmp_path / "one" / "two" / "a.json"
        assert path.read_text(encoding="utf-8") == "{}"

    def test_a_write_overwrites_an_existing_file(self, tmp_path: Path) -> None:
        folder = SchemaFolder(tmp_path)
        folder.write("a.json", "old")
        folder.write("a.json", "new")
        assert folder.read("a.json") == "new"

    def test_line_endings_are_kept_byte_for_byte(self, tmp_path: Path) -> None:
        folder = SchemaFolder(tmp_path)
        path = folder.write("a.json", "{\n}\n")
        assert path.read_bytes() == b"{\n}\n"

    def test_reading_a_folder_is_unreadable(self, tmp_path: Path) -> None:
        (tmp_path / "sub").mkdir()
        with pytest.raises(SESchemaUnreadableError) as info:
            SchemaFolder(tmp_path).read("sub")
        assert info.value.__cause__ is not None
        assert isinstance(info.value, SESchemaError)

    def test_reading_bytes_that_are_not_utf_8_is_unreadable(self, tmp_path: Path) -> None:
        (tmp_path / "bad.json").write_bytes(b"\xff\xfe\xfa")
        with pytest.raises(SESchemaUnreadableError) as info:
            SchemaFolder(tmp_path).read("bad.json")
        assert info.value.__cause__ is not None

    def test_writing_under_a_root_that_is_a_file_is_unwritable(self, tmp_path: Path) -> None:
        root = tmp_path / "file"
        root.write_text("x", encoding="utf-8")
        with pytest.raises(SESchemaUnwritableError) as info:
            SchemaFolder(root).write("a.json", "{}")
        assert info.value.__cause__ is not None
        assert isinstance(info.value, SESchemaError)

    def test_a_write_logs_an_info_record_naming_the_file(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        folder = SchemaFolder(tmp_path, logging.getLogger("tests.schema_folder.info"))
        with caplog.at_level(logging.INFO, logger="tests.schema_folder.info"):
            folder.write("named.json", "{}")
        records = [r for r in caplog.records if r.levelno == logging.INFO]
        assert any("named.json" in r.getMessage() for r in records)
