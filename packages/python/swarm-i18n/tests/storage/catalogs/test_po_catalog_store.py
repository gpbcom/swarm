from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar

# Third-party imports
import pytest
from babel.messages.catalog import Catalog

# First-party imports
from swarm_i18n.models.catalogs.exceptions import SECatalogError, SECatalogUnreadableError  # isort: skip
from swarm_i18n.storage.catalogs.po_catalog_store import PoCatalogStore  # isort: skip
from swarm_models.models.enums import Language


class TestPoCatalogStore:
    MESSAGE_ID: ClassVar[str] = "Language: {language}"
    TEMPLATE_FILE: ClassVar[str] = "swarm.pot"
    PO_FILE: ClassVar[str] = "swarm.po"
    MESSAGES_FOLDER: ClassVar[str] = "LC_MESSAGES"

    def translation_of(self, language: Language) -> str:
        return f"{language.value}: {{language}}"

    def test_the_domain_is_swarm(self) -> None:
        assert PoCatalogStore.DOMAIN == "swarm"

    def test_the_template_holds_the_message_id(self, locales: Path) -> None:
        template = PoCatalogStore(locales).template()
        assert isinstance(template, Catalog)
        assert self.MESSAGE_ID in template

    def test_the_french_catalog_holds_its_translation(self, locales: Path) -> None:
        catalog = PoCatalogStore(locales).catalog(Language.FRENCH)
        assert isinstance(catalog, Catalog)
        message = catalog.get(self.MESSAGE_ID)
        assert message is not None
        assert message.string == self.translation_of(Language.FRENCH)

    @pytest.mark.parametrize("language", list(Language))
    def test_every_language_has_its_catalog(self, locales: Path, language: Language) -> None:
        message = PoCatalogStore(locales).catalog(language).get(self.MESSAGE_ID)
        assert message is not None
        assert message.string == self.translation_of(language)

    def test_a_missing_catalog_is_unreadable(self, locales_without_french: Path) -> None:
        with pytest.raises(SECatalogUnreadableError) as raised:
            PoCatalogStore(locales_without_french).catalog(Language.FRENCH)
        assert isinstance(raised.value, SECatalogError)
        assert raised.value.__cause__ is not None

    def test_a_malformed_catalog_is_unreadable(self, locales_with_malformed_french: Path) -> None:
        with pytest.raises(SECatalogUnreadableError) as raised:
            PoCatalogStore(locales_with_malformed_french).catalog(Language.FRENCH)
        assert isinstance(raised.value, SECatalogError)
        assert raised.value.__cause__ is not None

    def test_a_missing_template_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SECatalogUnreadableError) as raised:
            PoCatalogStore(tmp_path).template()
        assert raised.value.__cause__ is not None

    def test_the_default_root_is_the_locales_folder_of_the_package(self) -> None:
        root = PoCatalogStore.DEFAULT_ROOT
        assert root.parts[-2:] == ("swarm_i18n", "locales")
        assert (root / self.TEMPLATE_FILE).is_file()
        for language in Language:
            assert (root / language.value / self.MESSAGES_FOLDER / self.PO_FILE).is_file()
