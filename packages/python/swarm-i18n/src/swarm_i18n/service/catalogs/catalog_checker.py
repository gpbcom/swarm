from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from pathlib import Path
from typing import List, Optional

# Third-party imports
from babel.messages.catalog import Catalog, Message

# First-party imports
from swarm_i18n.models.enums import MessageProblem  # isort: skip
from swarm_i18n.models.translations.missing_translation import MissingTranslation  # isort: skip
from swarm_i18n.storage.catalogs.po_catalog_store import PoCatalogStore  # isort: skip
from swarm_models.enums import Language


class CatalogChecker:
    """Finds the messages of the template that have no usable translation.

    Attributes:
        store (PoCatalogStore): Where the catalogues are read.
        logger (Logger): Logger instance.

    Notes:
        - Problems come in template order, then in the order of the ``Language`` enum.
        - Storage errors propagate unchanged.
    """

    def __init__(self, store: PoCatalogStore, logger: Optional[Logger] = None) -> None:
        self.store = store
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _problem(self, catalog: Catalog, message_id: str) -> Optional[MessageProblem]:
        """Find what is wrong with one message in one catalogue.

        Args:
            catalog (Catalog): The catalogue of a language.
            message_id (str): The message identifier.

        Returns:
            Optional[MessageProblem]: The problem, or None when the message is usable.
        """
        entry = catalog.get(message_id)
        if entry is None:
            self.logger.debug("Message %s is absent.", message_id)
            return MessageProblem.MISSING
        if not str(entry.string).strip():
            self.logger.debug("Message %s has an empty translation.", message_id)
            return MessageProblem.EMPTY
        if entry.fuzzy:
            self.logger.debug("Message %s is fuzzy.", message_id)
            return MessageProblem.FUZZY
        self.logger.debug("Message %s is usable.", message_id)
        return None

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def at(cls, root: Optional[Path] = None) -> CatalogChecker:
        """Build a checker that reads the catalogues under a folder.

        Args:
            root (Optional[Path]): The folder of the catalogues, None for the default one.

        Returns:
            CatalogChecker: The checker.
        """
        logger = getLogger(__name__)
        if root is None:
            logger.debug("No root given, using the default catalogue root.")
            return cls(PoCatalogStore(PoCatalogStore.DEFAULT_ROOT))
        logger.debug("Using the catalogue root %s.", root)
        return cls(PoCatalogStore(root))

    def find_missing(self) -> List[MissingTranslation]:
        """List every message without a usable translation.

        Returns:
            List[MissingTranslation]: The problems found, empty when the catalogues are complete.
        """
        template = self.store.template()
        catalogs = {language: self.store.catalog(language) for language in Language}
        found: List[MissingTranslation] = []
        message: Message
        for message in template:
            message_id = str(message.id)
            if not message_id:
                self.logger.debug("Skipping the header entry.")
                continue
            for language in Language:
                problem = self._problem(catalogs[language], message_id)
                if problem is None:
                    self.logger.debug("Message %s is complete in %s.", message_id, language.value)
                    continue
                self.logger.debug("Message %s is %s in %s.", message_id, problem.value, language.value)
                found.append(MissingTranslation(message_id=message_id, language=language, problem=problem))
        self.logger.info("Found %d missing translations.", len(found))
        return found
