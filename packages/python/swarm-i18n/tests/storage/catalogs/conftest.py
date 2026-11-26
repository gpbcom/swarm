from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Optional

# Third-party imports
import pytest

# First-party imports
from swarm_models.models.enums import Language

MESSAGE_ID = "Language: {language}"
HEADER = 'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
TEMPLATE = HEADER + f'msgid "{MESSAGE_ID}"\nmsgstr ""\n'
MALFORMED_PO = HEADER + 'msgid "unterminated\nmsgstr "\n'


def write_po(root: Path, language: Language, content: str) -> None:
    path = root / language.value / "LC_MESSAGES" / "swarm.po"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_locales(root: Path, skipped: Optional[Language] = None) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "swarm.pot").write_text(TEMPLATE, encoding="utf-8")
    for language in Language:
        if language is not skipped:
            write_po(root, language, HEADER + f'msgid "{MESSAGE_ID}"\nmsgstr "{language.value}: {{language}}"\n')


@pytest.fixture
def locales(tmp_path: Path) -> Path:
    root = tmp_path / "locales"
    write_locales(root)
    return root


@pytest.fixture
def locales_without_french(tmp_path: Path) -> Path:
    root = tmp_path / "locales"
    write_locales(root, skipped=Language.FRENCH)
    return root


@pytest.fixture
def locales_with_malformed_french(tmp_path: Path) -> Path:
    root = tmp_path / "locales"
    write_locales(root, skipped=Language.FRENCH)
    write_po(root, Language.FRENCH, MALFORMED_PO)
    return root
