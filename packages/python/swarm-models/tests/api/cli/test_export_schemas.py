from __future__ import annotations

from importlib.metadata import entry_points
from pathlib import Path

import pytest

from swarm_models.api.cli.export_schemas import main


class TestExportSchemas:
    FILE_NAME = "swarm_models.schema.json"

    def test_a_write_creates_the_bundle_and_names_it(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        code = main(["--output", str(tmp_path)])

        assert code == 0
        assert (tmp_path / self.FILE_NAME).is_file()
        assert self.FILE_NAME in capsys.readouterr().out

    def test_check_on_an_empty_folder_fails_and_names_the_command(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        code = main(["--check", "--output", str(tmp_path)])

        assert code == 1
        assert "swarm-models-schemas" in capsys.readouterr().err
        assert not (tmp_path / self.FILE_NAME).exists()

    def test_check_passes_after_a_write(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        main(["--output", str(tmp_path)])
        capsys.readouterr()

        code = main(["--check", "--output", str(tmp_path)])

        assert code == 0
        assert "is up to date." in capsys.readouterr().out

    def test_check_fails_after_the_file_was_changed(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        main(["--output", str(tmp_path)])
        path = tmp_path / self.FILE_NAME
        path.write_text(path.read_text(encoding="utf-8") + "\n ", encoding="utf-8")
        capsys.readouterr()

        code = main(["--check", "--output", str(tmp_path)])

        assert code == 1
        assert "is out of date." in capsys.readouterr().err

    def test_an_output_that_is_a_file_returns_two(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        target = tmp_path / "not_a_folder"
        target.write_text("x", encoding="utf-8")

        code = main(["--output", str(target)])

        assert code == 2
        assert capsys.readouterr().err != ""

    def test_an_unknown_argument_ends_with_exit_code_two(self) -> None:
        with pytest.raises(SystemExit) as raised:
            main(["--unknown"])

        assert raised.value.code == 2

    def test_the_console_script_points_to_main(self) -> None:
        scripts = entry_points(group="console_scripts")

        assert scripts["swarm-models-schemas"].value == "swarm_models.api.cli.export_schemas:main"

    def test_the_committed_bundle_is_up_to_date(self) -> None:
        assert main(["--check"]) == 0
