from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.enums import Language, MessageProblem
from swarm_models.i18n.translations.exceptions import (
    SEInvalidMissingTranslationException,
    SEMissingTranslationInvalidLanguage,
    SEMissingTranslationInvalidMessageId,
    SEMissingTranslationInvalidProblem,
)
from swarm_models.i18n.translations.missing_translation import MissingTranslation


class TestMissingTranslation:
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "message_id": "mission.aborted",
        "language": Language.FRENCH,
        "problem": MessageProblem.MISSING,
    }

    def build(self, **changes: JsonValue) -> MissingTranslation:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return MissingTranslation.model_validate(values)

    @pytest.mark.parametrize("name", ["message_id", "language", "problem"])
    def test_defaults(self, name: str) -> None:
        values: Dict[str, JsonValue] = dict(self.VALID)
        del values[name]
        with pytest.raises((ValidationError, SEInvalidMissingTranslationException)):
            MissingTranslation.model_validate(values)

    def test_full_valid_construction(self) -> None:
        missing = self.build()
        assert missing.message_id == self.VALID["message_id"]
        assert missing.language == Language.FRENCH
        assert missing.problem == MessageProblem.MISSING

    @pytest.mark.parametrize("language", list(Language))
    def test_every_language_is_accepted(self, language: Language) -> None:
        assert self.build(language=language).language == language

    @pytest.mark.parametrize("language", list(Language))
    def test_the_value_string_of_a_language_is_accepted(self, language: Language) -> None:
        assert self.build(language=language.value).language == language

    @pytest.mark.parametrize("problem", list(MessageProblem))
    def test_the_value_string_of_a_problem_is_accepted(self, problem: MessageProblem) -> None:
        assert self.build(problem=problem.value).problem == problem

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("message_id", None, SEMissingTranslationInvalidMessageId),
            ("message_id", "", SEMissingTranslationInvalidMessageId),
            ("message_id", "   ", SEMissingTranslationInvalidMessageId),
            ("message_id", 3, SEMissingTranslationInvalidMessageId),
            ("message_id", True, SEMissingTranslationInvalidMessageId),
            ("language", None, SEMissingTranslationInvalidLanguage),
            ("language", "", SEMissingTranslationInvalidLanguage),
            ("language", "klingon", SEMissingTranslationInvalidLanguage),
            ("language", 3, SEMissingTranslationInvalidLanguage),
            ("language", True, SEMissingTranslationInvalidLanguage),
            ("problem", None, SEMissingTranslationInvalidProblem),
            ("problem", "", SEMissingTranslationInvalidProblem),
            ("problem", "broken", SEMissingTranslationInvalidProblem),
            ("problem", 3, SEMissingTranslationInvalidProblem),
            ("problem", True, SEMissingTranslationInvalidProblem),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    @pytest.mark.parametrize(
        "error",
        [
            SEMissingTranslationInvalidMessageId,
            SEMissingTranslationInvalidLanguage,
            SEMissingTranslationInvalidProblem,
        ],
    )
    def test_every_field_error_is_a_missing_translation_exception(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidMissingTranslationException)

    def test_the_message_id_is_stripped(self) -> None:
        assert self.build(message_id="  mission.aborted  ").message_id == "mission.aborted"

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_assigning_a_field_of_a_built_model_is_refused(self) -> None:
        missing = self.build()
        with pytest.raises(ValidationError):
            missing.problem = MessageProblem.EMPTY

    def test_round_trip(self) -> None:
        missing = self.build()
        assert MissingTranslation.model_validate(missing.model_dump()) == missing
        assert MissingTranslation.model_validate_json(missing.model_dump_json()) == missing
