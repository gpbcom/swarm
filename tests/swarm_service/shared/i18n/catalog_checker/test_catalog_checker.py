from __future__ import annotations

# Standard library imports
from typing import Callable, ClassVar, Dict, List, Tuple

# First-party imports
from swarm_models.enums import Language, MessageProblem
from swarm_models.i18n.translations.missing_translation import MissingTranslation
from swarm_service.shared.i18n.catalog_checker import CatalogChecker
from swarm_storage.shared.i18n.po_catalog_store import PoCatalogStore

Entries = Dict[Language, List[Tuple[str, str, bool]]]
StoreBuilder = Callable[[List[str], Entries], PoCatalogStore]


class TestCatalogChecker:
    COMPLETE: ClassVar[List[str]] = ["greeting", "farewell"]
    NEW: ClassVar[str] = "welcome"

    def copy(self, entries: Entries) -> Entries:
        return {language: list(items) for language, items in entries.items()}

    def test_complete_catalogues_give_nothing(self, write_store: StoreBuilder, complete_entries: Entries) -> None:
        store = write_store(self.COMPLETE, complete_entries)
        assert CatalogChecker(store).find_missing() == []

    def test_a_message_in_english_only_is_missing_in_the_three_other_languages(
        self, write_store: StoreBuilder, complete_entries: Entries
    ) -> None:
        entries = self.copy(complete_entries)
        entries[Language.ENGLISH].append((self.NEW, "Welcome", False))
        store = write_store([*self.COMPLETE, self.NEW], entries)
        assert CatalogChecker(store).find_missing() == [
            MissingTranslation(message_id=self.NEW, language=language, problem=MessageProblem.MISSING)
            for language in (Language.FRENCH, Language.GERMAN, Language.SPANISH)
        ]

    def test_an_empty_translation_is_reported_as_empty(
        self, write_store: StoreBuilder, complete_entries: Entries
    ) -> None:
        entries = self.copy(complete_entries)
        entries[Language.GERMAN][0] = (self.COMPLETE[0], "", False)
        store = write_store(self.COMPLETE, entries)
        assert CatalogChecker(store).find_missing() == [
            MissingTranslation(message_id=self.COMPLETE[0], language=Language.GERMAN, problem=MessageProblem.EMPTY)
        ]

    def test_a_fuzzy_translation_is_reported_as_fuzzy(
        self, write_store: StoreBuilder, complete_entries: Entries
    ) -> None:
        entries = self.copy(complete_entries)
        entries[Language.SPANISH][1] = (self.COMPLETE[1], "adios", True)
        store = write_store(self.COMPLETE, entries)
        assert CatalogChecker(store).find_missing() == [
            MissingTranslation(message_id=self.COMPLETE[1], language=Language.SPANISH, problem=MessageProblem.FUZZY)
        ]

    def test_problems_come_in_template_order_then_language_order(
        self, write_store: StoreBuilder, complete_entries: Entries
    ) -> None:
        entries = self.copy(complete_entries)
        entries[Language.FRENCH][1] = (self.COMPLETE[1], "", False)
        entries[Language.GERMAN][0] = (self.COMPLETE[0], "", False)
        entries[Language.ENGLISH][0] = (self.COMPLETE[0], "", False)
        store = write_store(self.COMPLETE, entries)
        found = CatalogChecker(store).find_missing()
        assert [(item.message_id, item.language) for item in found] == [
            (self.COMPLETE[0], Language.ENGLISH),
            (self.COMPLETE[0], Language.GERMAN),
            (self.COMPLETE[1], Language.FRENCH),
        ]

    def test_the_shipped_catalogues_are_complete(self) -> None:
        store = PoCatalogStore(PoCatalogStore.DEFAULT_ROOT)
        assert CatalogChecker(store).find_missing() == []
