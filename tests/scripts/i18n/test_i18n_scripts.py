from __future__ import annotations

# Standard library imports
from pathlib import Path

# Third-party imports
import pytest

# First-party imports
from swarm_i18n.api.cli.check_catalogs import main  # isort: skip
from swarm_models.enums import Language


class TestCheckCatalogs:
    def test_a_message_in_english_only_gives_exit_one(
        self, english_only_locales: Path, message_id: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert main(["--locales", str(english_only_locales)]) == 1
        stderr = capsys.readouterr().err
        assert message_id in stderr
        assert Language.FRENCH.value in stderr
        assert Language.GERMAN.value in stderr
        assert Language.SPANISH.value in stderr

    def test_one_line_is_printed_per_missing_translation(
        self, english_only_locales: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        main(["--locales", str(english_only_locales)])
        lines = [line for line in capsys.readouterr().err.splitlines() if line.strip()]
        assert len(lines) == 3

    def test_complete_catalogues_give_exit_zero(
        self, complete_locales: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert main(["--locales", str(complete_locales)]) == 0
        captured = capsys.readouterr()
        assert len(captured.out.strip().splitlines()) == 1
        assert captured.err == ""

    def test_a_malformed_catalogue_gives_exit_two(
        self, malformed_locales: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert main(["--locales", str(malformed_locales)]) == 2
        assert capsys.readouterr().err.strip()

    def test_without_argument_the_shipped_catalogues_give_exit_zero(self) -> None:
        assert main([]) == 0
