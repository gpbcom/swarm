from __future__ import annotations

# Standard library imports
from functools import partial
from pathlib import Path
from typing import Callable, Dict, List, Tuple

# Third-party imports
import pytest

# First-party imports
from swarm_i18n.storage.catalogs.po_catalog_store import PoCatalogStore
from swarm_models.models.enums import Language

HEADER = 'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
COMPLETE_IDS = ["greeting", "farewell"]


def render_po(entries: List[Tuple[str, str, bool]]) -> str:
    text = HEADER
    for message_id, translation, fuzzy in entries:
        if fuzzy:
            text += "#, fuzzy\n"
        text += f'msgid "{message_id}"\nmsgstr "{translation}"\n\n'
    return text


def build_store(
    root: Path, template_ids: List[str], entries: Dict[Language, List[Tuple[str, str, bool]]]
) -> PoCatalogStore:
    (root / "swarm.pot").write_text(render_po([(i, "", False) for i in template_ids]), encoding="utf-8")
    for language in Language:
        folder = root / language.value / "LC_MESSAGES"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "swarm.po").write_text(render_po(entries.get(language, [])), encoding="utf-8")
    return PoCatalogStore(root)


@pytest.fixture
def write_store(
    tmp_path: Path,
) -> Callable[[List[str], Dict[Language, List[Tuple[str, str, bool]]]], PoCatalogStore]:
    return partial(build_store, tmp_path)


@pytest.fixture
def complete_entries() -> Dict[Language, List[Tuple[str, str, bool]]]:
    return {
        language: [(message_id, f"{message_id} {language.value}", False) for message_id in COMPLETE_IDS]
        for language in Language
    }
