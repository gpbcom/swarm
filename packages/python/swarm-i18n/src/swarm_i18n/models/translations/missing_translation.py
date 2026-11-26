from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_i18n.models.enums import MessageProblem  # isort: skip
from swarm_i18n.models.translations.exceptions import (  # isort: skip
    SEMissingTranslationInvalidLanguage,
    SEMissingTranslationInvalidMessageId,
    SEMissingTranslationInvalidProblem,
)
from swarm_models.models.enums import Language


class MissingTranslation(BaseModel):
    """One message of a catalogue that has no usable translation in a language.

    Attributes:
        message_id (str): The identifier of the message.
        language (Language): The language in which the translation is missing.
        problem (MessageProblem): What is wrong with the message.
        MESSAGE_ID_FIELD (str): The name of the ``message_id`` field, for its validator.
        LANGUAGE_FIELD (str): The name of the ``language`` field, for its validator.
        PROBLEM_FIELD (str): The name of the ``problem`` field, for its validator.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - A boolean is refused where a string is expected.
        - The model is frozen, so a finding never changes once reported.
    """

    MESSAGE_ID_FIELD: ClassVar[str] = "message_id"
    LANGUAGE_FIELD: ClassVar[str] = "language"
    PROBLEM_FIELD: ClassVar[str] = "problem"
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    message_id: str = Field(description="The identifier of the message. Required.")
    language: Language = Field(description="The language in which the translation is missing. Required.")
    problem: MessageProblem = Field(description="What is wrong with the message. Required.")

    @field_validator(MESSAGE_ID_FIELD, mode=BEFORE)
    def validate_message_id(cls, value: JsonValue) -> JsonValue:
        """Validate ``message_id``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped message identifier.

        Raises:
            SEMissingTranslationInvalidMessageId: If the value is not a non-empty string.
        """
        if not isinstance(value, str) or not value.strip():
            raise SEMissingTranslationInvalidMessageId(f"Invalid message_id: {value!r}. Must be a non-empty string.")
        return value.strip()

    @field_validator(LANGUAGE_FIELD, mode=BEFORE)
    def validate_language(cls, value: JsonValue) -> JsonValue:
        """Validate ``language``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped language value.

        Raises:
            SEMissingTranslationInvalidLanguage: If the value is not a language.
        """
        if not isinstance(value, str) or value.strip() not in {member.value for member in Language}:
            raise SEMissingTranslationInvalidLanguage(
                f"Invalid language: {value!r}. Must be one of {[member.value for member in Language]}."
            )
        return value.strip()

    @field_validator(PROBLEM_FIELD, mode=BEFORE)
    def validate_problem(cls, value: JsonValue) -> JsonValue:
        """Validate ``problem``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped problem value.

        Raises:
            SEMissingTranslationInvalidProblem: If the value is not a message problem.
        """
        if not isinstance(value, str) or value.strip() not in {member.value for member in MessageProblem}:
            raise SEMissingTranslationInvalidProblem(
                f"Invalid problem: {value!r}. Must be one of {[member.value for member in MessageProblem]}."
            )
        return value.strip()
