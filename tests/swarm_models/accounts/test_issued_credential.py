from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List, Optional
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, SecretStr, ValidationError

# First-party imports
from swarm_nats.models.accounts.exceptions import (
    SEInvalidIssuedCredentialException,
    SEIssuedCredentialInconsistentKind,
    SEIssuedCredentialInvalidJwt,
    SEIssuedCredentialInvalidKind,
    SEIssuedCredentialInvalidName,
    SEIssuedCredentialInvalidOperatorId,
    SEIssuedCredentialInvalidPublicKey,
    SEIssuedCredentialInvalidSeed,
)
from swarm_nats.models.accounts.issued_credential import IssuedCredential
from swarm_nats.models.enums import CredentialKind


class TestIssuedCredential:
    OPERATOR_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    V4_ID: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"
    NAME: ClassVar[str] = "edge-node-1"
    PUBLIC_KEY: ClassVar[str] = "U" + "A" * 55
    SEED: ClassVar[str] = "SU" + "A" * 56
    JWT: ClassVar[str] = "a.b.c"
    OPERATOR_ID_FIELD: ClassVar[str] = "operator_id"
    KIND_FIELD: ClassVar[str] = "kind"
    NAME_FIELD: ClassVar[str] = "name"
    PUBLIC_KEY_FIELD: ClassVar[str] = "public_key"
    JWT_FIELD: ClassVar[str] = "jwt"
    SEED_FIELD: ClassVar[str] = "seed"
    FIELDS: ClassVar[List[str]] = [
        OPERATOR_ID_FIELD,
        KIND_FIELD,
        NAME_FIELD,
        PUBLIC_KEY_FIELD,
        JWT_FIELD,
        SEED_FIELD,
    ]
    VALID: ClassVar[Dict[str, JsonValue]] = {
        OPERATOR_ID_FIELD: OPERATOR_ID,
        KIND_FIELD: CredentialKind.EDGE,
        NAME_FIELD: NAME,
        PUBLIC_KEY_FIELD: PUBLIC_KEY,
        JWT_FIELD: JWT,
        SEED_FIELD: SEED,
    }
    OPERATOR_KINDS: ClassVar[List[CredentialKind]] = [
        CredentialKind.SERVICE,
        CredentialKind.EDGE,
        CredentialKind.SIMULATED,
    ]

    def valid(self) -> Dict[str, JsonValue]:
        return dict(self.VALID)

    def system(self) -> Dict[str, JsonValue]:
        data = self.valid()
        data[self.OPERATOR_ID_FIELD] = None
        data[self.KIND_FIELD] = CredentialKind.SYSTEM
        return data

    def test_defaults(self) -> None:
        for name in self.FIELDS:
            assert IssuedCredential.model_fields[name].is_required()

    def test_full_valid_construction(self) -> None:
        credential = IssuedCredential.model_validate(self.valid())
        assert credential.operator_id == UUID(self.OPERATOR_ID)
        assert credential.kind == CredentialKind.EDGE
        assert credential.name == self.NAME
        assert credential.public_key == self.PUBLIC_KEY
        assert credential.jwt == self.JWT
        assert isinstance(credential.seed, SecretStr)
        assert credential.seed.get_secret_value() == self.SEED

    def test_a_system_credential_has_no_operator(self) -> None:
        credential = IssuedCredential.model_validate(self.system())
        assert credential.operator_id is None
        assert credential.kind == CredentialKind.SYSTEM

    @pytest.mark.parametrize("kind", OPERATOR_KINDS)
    def test_every_operator_kind_is_accepted_with_an_operator(self, kind: CredentialKind) -> None:
        data = self.valid()
        data[self.KIND_FIELD] = kind
        assert IssuedCredential.model_validate(data).kind == kind

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            (KIND_FIELD, SEIssuedCredentialInvalidKind),
            (NAME_FIELD, SEIssuedCredentialInvalidName),
            (PUBLIC_KEY_FIELD, SEIssuedCredentialInvalidPublicKey),
            (JWT_FIELD, SEIssuedCredentialInvalidJwt),
            (SEED_FIELD, SEIssuedCredentialInvalidSeed),
        ],
    )
    def test_none_becomes_the_default(self, name: str, error: type[Exception]) -> None:
        """No field but the operator has a default, so None is refused with the exception of that field."""
        data = self.valid()
        data[name] = None
        with pytest.raises(error):
            IssuedCredential.model_validate(data)

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            (OPERATOR_ID_FIELD, V4_ID, SEIssuedCredentialInvalidOperatorId),
            (OPERATOR_ID_FIELD, "not-a-uuid", SEIssuedCredentialInvalidOperatorId),
            (OPERATOR_ID_FIELD, 7, SEIssuedCredentialInvalidOperatorId),
            (OPERATOR_ID_FIELD, True, SEIssuedCredentialInvalidOperatorId),
            (KIND_FIELD, "unknown", SEIssuedCredentialInvalidKind),
            (KIND_FIELD, "", SEIssuedCredentialInvalidKind),
            (KIND_FIELD, 3, SEIssuedCredentialInvalidKind),
            (NAME_FIELD, "", SEIssuedCredentialInvalidName),
            (NAME_FIELD, "   ", SEIssuedCredentialInvalidName),
            (NAME_FIELD, "edge node", SEIssuedCredentialInvalidName),
            (NAME_FIELD, "edge\tnode", SEIssuedCredentialInvalidName),
            (NAME_FIELD, 3, SEIssuedCredentialInvalidName),
            (PUBLIC_KEY_FIELD, "", SEIssuedCredentialInvalidPublicKey),
            (PUBLIC_KEY_FIELD, "A" + "A" * 55, SEIssuedCredentialInvalidPublicKey),
            (PUBLIC_KEY_FIELD, "U" + "A" * 54, SEIssuedCredentialInvalidPublicKey),
            (PUBLIC_KEY_FIELD, "U" + "a" * 55, SEIssuedCredentialInvalidPublicKey),
            (PUBLIC_KEY_FIELD, 3, SEIssuedCredentialInvalidPublicKey),
            (JWT_FIELD, "", SEIssuedCredentialInvalidJwt),
            (JWT_FIELD, "a.b", SEIssuedCredentialInvalidJwt),
            (JWT_FIELD, "a.b.c.d", SEIssuedCredentialInvalidJwt),
            (JWT_FIELD, "a.b.c!", SEIssuedCredentialInvalidJwt),
            (JWT_FIELD, 3, SEIssuedCredentialInvalidJwt),
            (SEED_FIELD, "", SEIssuedCredentialInvalidSeed),
            (SEED_FIELD, "SA" + "A" * 56, SEIssuedCredentialInvalidSeed),
            (SEED_FIELD, "SU" + "A" * 55, SEIssuedCredentialInvalidSeed),
            (SEED_FIELD, "SU" + "a" * 56, SEIssuedCredentialInvalidSeed),
            (SEED_FIELD, 3, SEIssuedCredentialInvalidSeed),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        data = self.valid()
        data[name] = value
        with pytest.raises(error):
            IssuedCredential.model_validate(data)

    @pytest.mark.parametrize(
        ("operator_id", "kind"),
        [
            (None, CredentialKind.SERVICE),
            (None, CredentialKind.EDGE),
            (None, CredentialKind.SIMULATED),
            (OPERATOR_ID, CredentialKind.SYSTEM),
        ],
    )
    def test_the_kind_is_system_if_and_only_if_there_is_no_operator(
        self, operator_id: Optional[str], kind: CredentialKind
    ) -> None:
        data = self.valid()
        data[self.OPERATOR_ID_FIELD] = operator_id
        data[self.KIND_FIELD] = kind
        with pytest.raises(SEIssuedCredentialInconsistentKind):
            IssuedCredential.model_validate(data)

    def test_rejects_unknown_keys(self) -> None:
        data = self.valid()
        data["extra"] = 1
        with pytest.raises(ValidationError):
            IssuedCredential.model_validate(data)

    def test_is_frozen(self) -> None:
        credential = IssuedCredential.model_validate(self.valid())
        with pytest.raises(ValidationError):
            credential.name = self.NAME

    @pytest.mark.parametrize("system", [False, True])
    def test_round_trip(self, system: bool) -> None:
        data = self.system() if system else self.valid()
        credential = IssuedCredential.model_validate(data)
        dumped = credential.model_dump()
        assert isinstance(dumped[self.SEED_FIELD], SecretStr)
        assert IssuedCredential.model_validate(dumped) == credential

    def test_repr_and_str_never_contain_the_seed(self) -> None:
        credential = IssuedCredential.model_validate(self.valid())
        assert self.SEED not in repr(credential)
        assert self.SEED not in str(credential)

    @pytest.mark.parametrize(
        "error",
        [
            SEIssuedCredentialInvalidOperatorId,
            SEIssuedCredentialInvalidKind,
            SEIssuedCredentialInvalidName,
            SEIssuedCredentialInvalidPublicKey,
            SEIssuedCredentialInvalidJwt,
            SEIssuedCredentialInvalidSeed,
            SEIssuedCredentialInconsistentKind,
        ],
    )
    def test_every_field_exception_belongs_to_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidIssuedCredentialException)
