from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Dict, Optional

# Third-party imports
from babel.messages.catalog import Catalog

# First-party imports
from swarm_models.enums import Language
from swarm_models.i18n.catalogs.exceptions import SECatalogUnknownMessageError
from swarm_models.people.person import Person
from swarm_storage.shared.i18n.po_catalog_store import PoCatalogStore


class Translator:
    """Gives the text of a message in a language.

    Attributes:
        store (PoCatalogStore): Where the catalogues are read.
        template (Optional[Catalog]): The template, read on first use.
        catalogs (Dict[Language, Catalog]): The catalogues already read.
        logger (Logger): Logger instance.

    Notes:
        - Each catalogue is read once and kept.
        - An empty translation falls back to English,
          a degraded result the code recovers from.
        - Storage errors propagate unchanged.
    """

    def __init__(self, store: PoCatalogStore, logger: Optional[Logger] = None) -> None:
        self.store = store
        self.template: Optional[Catalog] = None
        self.catalogs: Dict[Language, Catalog] = {}
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _catalog(self, language: Language) -> Catalog:
        """Get the catalogue of a language, reading it the first time.

        Args:
            language (Language): The language wanted.

        Returns:
            Catalog: The catalogue.
        """
        if language not in self.catalogs:
            self.logger.debug("Reading the catalogue of %s.", language.value)
            self.catalogs[language] = self.store.catalog(language)
        else:
            self.logger.debug("Using the kept catalogue of %s.", language.value)
        return self.catalogs[language]

    def _text(self, message_id: str, language: Language) -> str:
        """Get the translation of a message, possibly empty.

        Args:
            message_id (str): The message identifier.
            language (Language): The language wanted.

        Returns:
            str: The translation, empty when there is none.
        """
        entry = self._catalog(language).get(message_id)
        if entry is None:
            self.logger.debug("Message %s is absent from %s.", message_id, language.value)
            return ""
        self.logger.debug("Message %s found in %s.", message_id, language.value)
        return str(entry.string)

    ############################
    # Publicly Exposed Methods #
    ############################

    def translate(self, message_id: str, language: Language) -> str:
        """Translate one message.

        Args:
            message_id (str): The message identifier.
            language (Language): The language wanted.

        Returns:
            str: The translation, or the English text when the translation is empty.

        Raises:
            SECatalogUnknownMessageError: When the id is not in the template.
        """
        if self.template is None:
            self.logger.debug("Reading the template.")
            self.template = self.store.template()
        if message_id not in self.template:
            self.logger.error("Message %s is not in the template.", message_id)
            raise SECatalogUnknownMessageError(f"Unknown message: {message_id!r}.")
        text = self._text(message_id, language)
        if text.strip():
            self.logger.debug("Translated %s into %s.", message_id, language.value)
            return text
        self.logger.warning("Message %s has no translation in %s, using English.", message_id, language.value)
        return self._text(message_id, Language.ENGLISH)

    def translate_for(self, person: Person, message_id: str) -> str:
        """Translate one message into the language of a person.

        Args:
            person (Person): The person who reads it.
            message_id (str): The message identifier.

        Returns:
            str: The translation.
        """
        self.logger.debug("Translating %s for the language of the person.", message_id)
        return self.translate(message_id, person.language)
