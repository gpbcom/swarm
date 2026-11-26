from __future__ import annotations

# First-party imports
from swarm_models.i18n.translations.exceptions.se_invalid_missing_translation_exception import (
    SEInvalidMissingTranslationException,
)


class SEMissingTranslationInvalidMessageId(SEInvalidMissingTranslationException):
    """Exception raised when an invalid ``message_id`` is provided."""
