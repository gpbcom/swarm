from __future__ import annotations

# Standard library imports
import re
from enum import StrEnum
from typing import ClassVar, Dict, List

# Third-party imports
import pytest

# First-party imports
from gateway.models.enums import AccessRefusal, TokenClaim


class TestGatewayEnums:
    SNAKE_CASE: ClassVar[re.Pattern[str]] = re.compile(r"^[a-z]+(_[a-z]+)*$")
    REFUSALS: ClassVar[Dict[str, str]] = {
        "MISSING_TOKEN": "missing_token",
        "INVALID_TOKEN": "invalid_token",
        "EXPIRED_TOKEN": "expired_token",
        "WRONG_OPERATOR": "wrong_operator",
        "MISSING_ROLE": "missing_role",
        "IDENTITY_UNAVAILABLE": "identity_unavailable",
    }
    CLAIMS: ClassVar[Dict[str, str]] = {
        "SUBJECT": "sub",
        "ISSUER": "iss",
        "AUDIENCE": "aud",
        "EXPIRES_AT": "exp",
        "ISSUED_AT": "iat",
        "OPERATOR_ID": "operator_id",
        "REALM_ACCESS": "realm_access",
        "ROLES": "roles",
    }
    ENUMS: ClassVar[List[type[StrEnum]]] = [AccessRefusal, TokenClaim]

    def test_access_refusal_has_exactly_its_members(self) -> None:
        assert {member.name: member.value for member in AccessRefusal} == self.REFUSALS

    def test_token_claim_has_exactly_its_members(self) -> None:
        assert {member.name: member.value for member in TokenClaim} == self.CLAIMS

    @pytest.mark.parametrize("enum", ENUMS)
    def test_values_are_lower_case_words_without_a_hyphen(self, enum: type[StrEnum]) -> None:
        for member in enum:
            assert self.SNAKE_CASE.match(member.value)
            assert "-" not in member.value

    @pytest.mark.parametrize("enum", ENUMS)
    def test_values_are_unique(self, enum: type[StrEnum]) -> None:
        values = [member.value for member in enum]
        assert len(values) == len(set(values))

    @pytest.mark.parametrize("enum", ENUMS)
    def test_members_are_strings(self, enum: type[StrEnum]) -> None:
        for member in enum:
            assert isinstance(member, str)
