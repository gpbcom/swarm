from __future__ import annotations

# Standard library imports
from enum import StrEnum
from typing import ClassVar, Dict, Type

# Third-party imports
import pytest

# First-party imports
from swarm_models.enums import CredentialKind, NatsClaimType, StreamRetention, StreamStorage


class TestSwarmModelsNatsEnums:
    EXPECTED: ClassVar[Dict[Type[StrEnum], Dict[str, str]]] = {
        CredentialKind: {"SERVICE": "service", "EDGE": "edge", "SIMULATED": "simulated", "SYSTEM": "system"},
        NatsClaimType: {"OPERATOR": "operator", "ACCOUNT": "account", "USER": "user"},
        StreamStorage: {"FILE": "file", "MEMORY": "memory"},
        StreamRetention: {"LIMITS": "limits", "INTEREST": "interest", "WORK_QUEUE": "work_queue"},
    }

    @pytest.mark.parametrize("enum", [CredentialKind, NatsClaimType, StreamStorage, StreamRetention])
    def test_the_members_and_values_are_exactly_the_contract(self, enum: Type[StrEnum]) -> None:
        assert {member.name: member.value for member in enum} == self.EXPECTED[enum]

    @pytest.mark.parametrize("enum", [CredentialKind, NatsClaimType, StreamStorage, StreamRetention])
    def test_each_enum_is_a_str_enum(self, enum: Type[StrEnum]) -> None:
        assert issubclass(enum, StrEnum)

    @pytest.mark.parametrize("enum", [CredentialKind, NatsClaimType, StreamStorage, StreamRetention])
    def test_no_value_contains_a_hyphen(self, enum: Type[StrEnum]) -> None:
        assert all("-" not in member.value for member in enum)
