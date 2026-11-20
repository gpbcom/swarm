from __future__ import annotations

from typing import ClassVar, Dict, List, Union

import pytest
from pydantic import JsonValue, SecretStr, ValidationError

from swarm_nats.models.accounts.exceptions import (
    SEInvalidIssuedAccountException,
    SEIssuedAccountInvalidJwt,
    SEIssuedAccountInvalidName,
    SEIssuedAccountInvalidPublicKey,
    SEIssuedAccountInvalidSeed,
)
from swarm_nats.models.accounts.issued_account import IssuedAccount


class TestIssuedAccount:
    OPERATOR_NAME: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    SYSTEM_NAME: ClassVar[str] = "SYS"
    PUBLIC_KEY: ClassVar[str] = "A" + "A" * 55
    SEED: ClassVar[str] = "SA" + "A" * 56
    JWT: ClassVar[str] = "a.b.c"
    NAME_FIELD: ClassVar[str] = "name"
    PUBLIC_KEY_FIELD: ClassVar[str] = "public_key"
    JWT_FIELD: ClassVar[str] = "jwt"
    SEED_FIELD: ClassVar[str] = "seed"
    FIELDS: ClassVar[List[str]] = [NAME_FIELD, PUBLIC_KEY_FIELD, JWT_FIELD, SEED_FIELD]
    VALID: ClassVar[Dict[str, JsonValue]] = {
        NAME_FIELD: OPERATOR_NAME,
        PUBLIC_KEY_FIELD: PUBLIC_KEY,
        JWT_FIELD: JWT,
        SEED_FIELD: SEED,
    }

    def valid(self) -> Dict[str, JsonValue]:
        return dict(self.VALID)

    def test_defaults(self) -> None:
        for name in self.FIELDS:
            assert IssuedAccount.model_fields[name].is_required()

    def test_full_valid_construction(self) -> None:
        account = IssuedAccount.model_validate(self.valid())
        assert account.name == self.OPERATOR_NAME
        assert account.public_key == self.PUBLIC_KEY
        assert account.jwt == self.JWT
        assert isinstance(account.seed, SecretStr)
        assert account.seed.get_secret_value() == self.SEED

    def test_the_name_is_stripped(self) -> None:
        data = self.valid()
        data[self.NAME_FIELD] = f"  {self.SYSTEM_NAME}  "
        assert IssuedAccount.model_validate(data).name == self.SYSTEM_NAME

    def test_a_secret_seed_is_accepted(self) -> None:
        data: Dict[str, Union[str, SecretStr]] = {
            self.NAME_FIELD: self.SYSTEM_NAME,
            self.PUBLIC_KEY_FIELD: self.PUBLIC_KEY,
            self.JWT_FIELD: self.JWT,
            self.SEED_FIELD: SecretStr(self.SEED),
        }
        account = IssuedAccount.model_validate(data)
        assert account.seed.get_secret_value() == self.SEED

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            (NAME_FIELD, SEIssuedAccountInvalidName),
            (PUBLIC_KEY_FIELD, SEIssuedAccountInvalidPublicKey),
            (JWT_FIELD, SEIssuedAccountInvalidJwt),
            (SEED_FIELD, SEIssuedAccountInvalidSeed),
        ],
    )
    def test_none_becomes_the_default(self, name: str, error: type[Exception]) -> None:
        """No field has a default, so None is refused with the exception of that field."""
        data = self.valid()
        data[name] = None
        with pytest.raises(error):
            IssuedAccount.model_validate(data)

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            (NAME_FIELD, "", SEIssuedAccountInvalidName),
            (NAME_FIELD, "   ", SEIssuedAccountInvalidName),
            (NAME_FIELD, 3, SEIssuedAccountInvalidName),
            (PUBLIC_KEY_FIELD, "", SEIssuedAccountInvalidPublicKey),
            (PUBLIC_KEY_FIELD, "O" + "A" * 55, SEIssuedAccountInvalidPublicKey),
            (PUBLIC_KEY_FIELD, "A" + "A" * 54, SEIssuedAccountInvalidPublicKey),
            (PUBLIC_KEY_FIELD, "A" + "a" * 55, SEIssuedAccountInvalidPublicKey),
            (PUBLIC_KEY_FIELD, "A" + "1" * 55, SEIssuedAccountInvalidPublicKey),
            (PUBLIC_KEY_FIELD, 3, SEIssuedAccountInvalidPublicKey),
            (JWT_FIELD, "", SEIssuedAccountInvalidJwt),
            (JWT_FIELD, "a.b", SEIssuedAccountInvalidJwt),
            (JWT_FIELD, "a.b.c.d", SEIssuedAccountInvalidJwt),
            (JWT_FIELD, "a.b.c!", SEIssuedAccountInvalidJwt),
            (JWT_FIELD, 3, SEIssuedAccountInvalidJwt),
            (SEED_FIELD, "", SEIssuedAccountInvalidSeed),
            (SEED_FIELD, "SO" + "A" * 56, SEIssuedAccountInvalidSeed),
            (SEED_FIELD, "SA" + "A" * 55, SEIssuedAccountInvalidSeed),
            (SEED_FIELD, "SA" + "a" * 56, SEIssuedAccountInvalidSeed),
            (SEED_FIELD, 3, SEIssuedAccountInvalidSeed),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        data = self.valid()
        data[name] = value
        with pytest.raises(error):
            IssuedAccount.model_validate(data)

    def test_rejects_unknown_keys(self) -> None:
        data = self.valid()
        data["extra"] = 1
        with pytest.raises(ValidationError):
            IssuedAccount.model_validate(data)

    def test_is_frozen(self) -> None:
        account = IssuedAccount.model_validate(self.valid())
        with pytest.raises(ValidationError):
            account.name = self.SYSTEM_NAME

    def test_round_trip(self) -> None:
        account = IssuedAccount.model_validate(self.valid())
        dumped = account.model_dump()
        assert isinstance(dumped[self.SEED_FIELD], SecretStr)
        assert IssuedAccount.model_validate(dumped) == account

    def test_repr_and_str_never_contain_the_seed(self) -> None:
        account = IssuedAccount.model_validate(self.valid())
        assert self.SEED not in repr(account)
        assert self.SEED not in str(account)

    @pytest.mark.parametrize(
        "error",
        [
            SEIssuedAccountInvalidName,
            SEIssuedAccountInvalidPublicKey,
            SEIssuedAccountInvalidJwt,
            SEIssuedAccountInvalidSeed,
        ],
    )
    def test_every_field_exception_belongs_to_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidIssuedAccountException)
