from __future__ import annotations

# Standard library imports
from typing import ClassVar, Optional

# Third-party imports
import pytest

# First-party imports
from swarm_i18n.models.catalogs.exceptions import SECatalogUnknownMessageError
from swarm_i18n.service.translations.translator import Translator
from swarm_i18n.storage.catalogs.po_catalog_store import PoCatalogStore
from swarm_models.models.enums import Language
from swarm_models.models.people.person import Person


class TestTranslator:
    ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    GREETING: ClassVar[str] = "greeting"
    PENDING: ClassVar[str] = "pending"
    PENDING_ENGLISH: ClassVar[str] = "Pending"
    UNKNOWN: ClassVar[str] = "not_in_the_template"

    def person(self, language: Optional[Language]) -> Person:
        data = {"id": self.ID, "name": "Ada Lovelace", "email": "ada@example.org"}
        if language is None:
            return Person.model_validate(data)
        return Person.model_validate({**data, "language": language})

    @pytest.mark.parametrize(
        ("language", "text"),
        [
            (Language.ENGLISH, "Hello"),
            (Language.FRENCH, "Bonjour"),
            (Language.GERMAN, "Hallo"),
            (Language.SPANISH, "Hola"),
        ],
    )
    def test_a_message_is_translated_into_the_language(
        self, store: PoCatalogStore, language: Language, text: str
    ) -> None:
        assert Translator(store).translate(self.GREETING, language) == text

    def test_a_person_gets_their_language(self, store: PoCatalogStore) -> None:
        person = self.person(Language.GERMAN)
        assert Translator(store).translate_for(person, self.GREETING) == "Hallo"

    def test_a_person_without_a_language_gets_english(self, store: PoCatalogStore) -> None:
        person = self.person(None)
        assert Translator(store).translate_for(person, self.GREETING) == "Hello"

    def test_an_unknown_message_is_refused(self, store: PoCatalogStore) -> None:
        with pytest.raises(SECatalogUnknownMessageError):
            Translator(store).translate(self.UNKNOWN, Language.FRENCH)

    def test_an_empty_translation_falls_back_to_english(self, store: PoCatalogStore) -> None:
        assert Translator(store).translate(self.PENDING, Language.GERMAN) == self.PENDING_ENGLISH
