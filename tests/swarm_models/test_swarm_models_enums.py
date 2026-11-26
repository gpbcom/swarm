from __future__ import annotations

# Standard library imports
from enum import StrEnum
from typing import List

# First-party imports
from swarm_models.models.enums import Language


class TestSwarmModelsEnums:
    def test_language_is_a_string_enum(self) -> None:
        assert issubclass(Language, StrEnum)

    def test_language_has_the_four_languages_in_order(self) -> None:
        members: List[Language] = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH]
        assert list(Language) == members
        assert [member.value for member in Language] == ["en", "fr", "de", "es"]

    def test_language_values_are_unique_lower_case_and_without_hyphen(self) -> None:
        values = [member.value for member in Language]
        assert len(set(values)) == len(values)
        assert all(value == value.lower() and "-" not in value for value in values)
