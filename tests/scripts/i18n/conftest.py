from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Dict

# Third-party imports
import pytest

# First-party imports
from swarm_models.enums import Language

MESSAGE_ID = "Language: {language}"
TRANSLATIONS: Dict[Language, str] = {
    Language.ENGLISH: "Language: {language}",
    Language.FRENCH: "Langue : {language}",
    Language.GERMAN: "Sprache: {language}",
    Language.SPANISH: "Idioma: {language}",
}
HEADER = 'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
MALFORMED_PO = HEADER + f'msgid "{MESSAGE_ID}"\nmsgstr[abc] "broken"\n'


def write_template(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "swarm.pot").write_text(HEADER + f'msgid "{MESSAGE_ID}"\nmsgstr ""\n', encoding="utf-8")


def write_catalog(root: Path, language: Language, content: str) -> None:
    folder = root / language.value / "LC_MESSAGES"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "swarm.po").write_text(content, encoding="utf-8")


def translated(text: str) -> str:
    return HEADER + f'msgid "{MESSAGE_ID}"\nmsgstr "{text}"\n'


@pytest.fixture
def message_id() -> str:
    return MESSAGE_ID


@pytest.fixture
def complete_locales(tmp_path: Path) -> Path:
    root = tmp_path / "complete"
    write_template(root)
    for language, text in TRANSLATIONS.items():
        write_catalog(root, language, translated(text))
    return root


@pytest.fixture
def english_only_locales(tmp_path: Path) -> Path:
    root = tmp_path / "english_only"
    write_template(root)
    write_catalog(root, Language.ENGLISH, translated(TRANSLATIONS[Language.ENGLISH]))
    for language in (Language.FRENCH, Language.GERMAN, Language.SPANISH):
        write_catalog(root, language, translated(""))
    return root


@pytest.fixture
def malformed_locales(tmp_path: Path) -> Path:
    root = tmp_path / "malformed"
    write_template(root)
    for language in (Language.ENGLISH, Language.GERMAN, Language.SPANISH):
        write_catalog(root, language, translated(TRANSLATIONS[language]))
    write_catalog(root, Language.FRENCH, MALFORMED_PO)
    return root
