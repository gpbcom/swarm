from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import Dict

# Third-party imports
import pytest

# First-party imports
from swarm_i18n.storage.catalogs.po_catalog_store import PoCatalogStore
from swarm_models.models.enums import Language

HEADER = 'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
GREETING = "greeting"
PENDING = "pending"
GREETINGS: Dict[Language, str] = {
    Language.ENGLISH: "Hello",
    Language.FRENCH: "Bonjour",
    Language.GERMAN: "Hallo",
    Language.SPANISH: "Hola",
}
PENDING_ENGLISH = "Pending"


@pytest.fixture
def store(tmp_path: Path) -> PoCatalogStore:
    template = HEADER + f'msgid "{GREETING}"\nmsgstr ""\n\nmsgid "{PENDING}"\nmsgstr ""\n\n'
    (tmp_path / "swarm.pot").write_text(template, encoding="utf-8")
    for language in Language:
        pending = PENDING_ENGLISH if language == Language.ENGLISH else ""
        text = HEADER + f'msgid "{GREETING}"\nmsgstr "{GREETINGS[language]}"\n\n'
        text += f'msgid "{PENDING}"\nmsgstr "{pending}"\n\n'
        folder = tmp_path / language.value / "LC_MESSAGES"
        folder.mkdir(parents=True)
        (folder / "swarm.po").write_text(text, encoding="utf-8")
    return PoCatalogStore(tmp_path)
