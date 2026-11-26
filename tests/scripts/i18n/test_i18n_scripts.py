from __future__ import annotations

# Standard library imports
from importlib.metadata import entry_points
from inspect import signature
from pathlib import Path
from typing import ClassVar

# Third-party imports
import pytest

# First-party imports
from swarm_models.enums import Language
from swarm_scripts.i18n.check import main
from swarm_service.shared.i18n.catalog_checker import CatalogChecker


class TestI18nScripts:
    SCRIPT: ClassVar[str] = "swarm-i18n-check"
    TARGET: ClassVar[str] = "swarm_scripts.i18n.check:main"

    @pytest.fixture(autouse=True)
    def no_entry(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(CatalogChecker.LOCALES_KEY, raising=False)

    def check(self, monkeypatch: pytest.MonkeyPatch, locales: Path) -> int:
        monkeypatch.setenv(CatalogChecker.LOCALES_KEY, str(locales))
        return main()

    def test_a_message_in_english_only_gives_exit_one(
        self,
        english_only_locales: Path,
        message_id: str,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        assert self.check(monkeypatch, english_only_locales) == 1
        stderr = capsys.readouterr().err
        assert message_id in stderr
        assert Language.FRENCH.value in stderr
        assert Language.GERMAN.value in stderr
        assert Language.SPANISH.value in stderr

    def test_one_line_is_printed_per_missing_translation(
        self, english_only_locales: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self.check(monkeypatch, english_only_locales)
        lines = [line for line in capsys.readouterr().err.splitlines() if line.strip()]
        assert len(lines) == 3

    def test_complete_catalogues_give_exit_zero(
        self, complete_locales: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        assert self.check(monkeypatch, complete_locales) == 0
        captured = capsys.readouterr()
        assert len(captured.out.strip().splitlines()) == 1
        assert captured.err == ""

    def test_a_malformed_catalogue_gives_exit_two(
        self, malformed_locales: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        assert self.check(monkeypatch, malformed_locales) == 2
        assert capsys.readouterr().err.strip()

    def test_without_the_entry_the_shipped_catalogues_give_exit_zero(self) -> None:
        assert main() == 0

    def test_main_takes_no_argument(self) -> None:
        assert not signature(main).parameters

    def test_the_console_script_points_to_main(self) -> None:
        assert entry_points(group="console_scripts")[self.SCRIPT].value == self.TARGET
