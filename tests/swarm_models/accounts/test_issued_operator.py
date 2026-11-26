from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List, Union

# Third-party imports
import pytest
from pydantic import JsonValue, SecretStr, ValidationError

# First-party imports
from swarm_models.accounts.exceptions import (
    SEInvalidIssuedOperatorException,
    SEIssuedAccountInvalidName,
    SEIssuedOperatorInvalidJwt,
    SEIssuedOperatorInvalidName,
    SEIssuedOperatorInvalidPublicKey,
    SEIssuedOperatorInvalidSeed,
    SEIssuedOperatorInvalidSystemAccount,
)
from swarm_models.accounts.issued_account import IssuedAccount
from swarm_models.accounts.issued_operator import IssuedOperator


class TestIssuedOperator:
    OPERATOR_NAME: ClassVar[str] = "swarm"
    PUBLIC_KEY: ClassVar[str] = "O" + "A" * 55
    SEED: ClassVar[str] = "SO" + "A" * 56
    JWT: ClassVar[str] = "a.b.c"
    ACCOUNT_NAME: ClassVar[str] = "SYS"
    ACCOUNT_PUBLIC_KEY: ClassVar[str] = "A" + "A" * 55
    ACCOUNT_SEED: ClassVar[str] = "SA" + "A" * 56
    NAME_FIELD: ClassVar[str] = "name"
    PUBLIC_KEY_FIELD: ClassVar[str] = "public_key"
    JWT_FIELD: ClassVar[str] = "jwt"
    SEED_FIELD: ClassVar[str] = "seed"
    SYSTEM_ACCOUNT_FIELD: ClassVar[str] = "system_account"
    FIELDS: ClassVar[List[str]] = [NAME_FIELD, PUBLIC_KEY_FIELD, JWT_FIELD, SEED_FIELD, SYSTEM_ACCOUNT_FIELD]
    ACCOUNT: ClassVar[Dict[str, JsonValue]] = {
        NAME_FIELD: ACCOUNT_NAME,
        PUBLIC_KEY_FIELD: ACCOUNT_PUBLIC_KEY,
        JWT_FIELD: JWT,
        SEED_FIELD: ACCOUNT_SEED,
    }
    VALID: ClassVar[Dict[str, JsonValue]] = {
        NAME_FIELD: OPERATOR_NAME,
        PUBLIC_KEY_FIELD: PUBLIC_KEY,
        JWT_FIELD: JWT,
        SEED_FIELD: SEED,
        SYSTEM_ACCOUNT_FIELD: ACCOUNT,
    }

    def valid(self) -> Dict[str, JsonValue]:
        return dict(self.VALID)

    def test_defaults(self) -> None:
        for name in self.FIELDS:
            assert IssuedOperator.model_fields[name].is_required()

    def test_full_valid_construction(self) -> None:
        operator = IssuedOperator.model_validate(self.valid())
        assert operator.name == self.OPERATOR_NAME
        assert operator.public_key == self.PUBLIC_KEY
        assert operator.jwt == self.JWT
        assert isinstance(operator.seed, SecretStr)
        assert operator.seed.get_secret_value() == self.SEED
        assert isinstance(operator.system_account, IssuedAccount)
        assert operator.system_account.name == self.ACCOUNT_NAME

    def test_the_name_is_stripped(self) -> None:
        data = self.valid()
        data[self.NAME_FIELD] = f"  {self.OPERATOR_NAME}  "
        assert IssuedOperator.model_validate(data).name == self.OPERATOR_NAME

    def test_a_secret_seed_is_accepted(self) -> None:
        data: Dict[str, Union[str, SecretStr, IssuedAccount]] = {
            self.NAME_FIELD: self.OPERATOR_NAME,
            self.PUBLIC_KEY_FIELD: self.PUBLIC_KEY,
            self.JWT_FIELD: self.JWT,
            self.SEED_FIELD: SecretStr(self.SEED),
            self.SYSTEM_ACCOUNT_FIELD: IssuedAccount.model_validate(self.ACCOUNT),
        }
        operator = IssuedOperator.model_validate(data)
        assert operator.seed.get_secret_value() == self.SEED

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            (NAME_FIELD, SEIssuedOperatorInvalidName),
            (PUBLIC_KEY_FIELD, SEIssuedOperatorInvalidPublicKey),
            (JWT_FIELD, SEIssuedOperatorInvalidJwt),
            (SEED_FIELD, SEIssuedOperatorInvalidSeed),
            (SYSTEM_ACCOUNT_FIELD, SEIssuedOperatorInvalidSystemAccount),
        ],
    )
    def test_none_becomes_the_default(self, name: str, error: type[Exception]) -> None:
        """No field has a default, so None is refused with the exception of that field."""
        data = self.valid()
        data[name] = None
        with pytest.raises(error):
            IssuedOperator.model_validate(data)

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            (NAME_FIELD, "", SEIssuedOperatorInvalidName),
            (NAME_FIELD, "   ", SEIssuedOperatorInvalidName),
            (NAME_FIELD, 3, SEIssuedOperatorInvalidName),
            (PUBLIC_KEY_FIELD, "", SEIssuedOperatorInvalidPublicKey),
            (PUBLIC_KEY_FIELD, "A" + "A" * 55, SEIssuedOperatorInvalidPublicKey),
            (PUBLIC_KEY_FIELD, "O" + "A" * 54, SEIssuedOperatorInvalidPublicKey),
            (PUBLIC_KEY_FIELD, "O" + "a" * 55, SEIssuedOperatorInvalidPublicKey),
            (PUBLIC_KEY_FIELD, "O" + "1" * 55, SEIssuedOperatorInvalidPublicKey),
            (PUBLIC_KEY_FIELD, 3, SEIssuedOperatorInvalidPublicKey),
            (JWT_FIELD, "", SEIssuedOperatorInvalidJwt),
            (JWT_FIELD, "a.b", SEIssuedOperatorInvalidJwt),
            (JWT_FIELD, "a.b.c.d", SEIssuedOperatorInvalidJwt),
            (JWT_FIELD, "a.b.c!", SEIssuedOperatorInvalidJwt),
            (JWT_FIELD, 3, SEIssuedOperatorInvalidJwt),
            (SEED_FIELD, "", SEIssuedOperatorInvalidSeed),
            (SEED_FIELD, "SA" + "A" * 56, SEIssuedOperatorInvalidSeed),
            (SEED_FIELD, "SO" + "A" * 55, SEIssuedOperatorInvalidSeed),
            (SEED_FIELD, "SO" + "a" * 56, SEIssuedOperatorInvalidSeed),
            (SEED_FIELD, 3, SEIssuedOperatorInvalidSeed),
            (SYSTEM_ACCOUNT_FIELD, "SYS", SEIssuedOperatorInvalidSystemAccount),
            (SYSTEM_ACCOUNT_FIELD, 3, SEIssuedOperatorInvalidSystemAccount),
            (SYSTEM_ACCOUNT_FIELD, ["SYS"], SEIssuedOperatorInvalidSystemAccount),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        data = self.valid()
        data[name] = value
        with pytest.raises(error):
            IssuedOperator.model_validate(data)

    def test_the_errors_of_the_system_account_are_raised_unchanged(self) -> None:
        account = dict(self.ACCOUNT)
        account[self.NAME_FIELD] = ""
        data = self.valid()
        data[self.SYSTEM_ACCOUNT_FIELD] = account
        with pytest.raises(SEIssuedAccountInvalidName):
            IssuedOperator.model_validate(data)

    def test_rejects_unknown_keys(self) -> None:
        data = self.valid()
        data["extra"] = 1
        with pytest.raises(ValidationError):
            IssuedOperator.model_validate(data)

    def test_is_frozen(self) -> None:
        operator = IssuedOperator.model_validate(self.valid())
        with pytest.raises(ValidationError):
            operator.name = self.ACCOUNT_NAME

    def test_round_trip(self) -> None:
        operator = IssuedOperator.model_validate(self.valid())
        dumped = operator.model_dump()
        assert isinstance(dumped[self.SEED_FIELD], SecretStr)
        assert IssuedOperator.model_validate(dumped) == operator

    def test_repr_and_str_never_contain_the_seed(self) -> None:
        operator = IssuedOperator.model_validate(self.valid())
        for text in (repr(operator), str(operator)):
            assert self.SEED not in text
            assert self.ACCOUNT_SEED not in text

    @pytest.mark.parametrize(
        "error",
        [
            SEIssuedOperatorInvalidName,
            SEIssuedOperatorInvalidPublicKey,
            SEIssuedOperatorInvalidJwt,
            SEIssuedOperatorInvalidSeed,
            SEIssuedOperatorInvalidSystemAccount,
        ],
    )
    def test_every_field_exception_belongs_to_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidIssuedOperatorException)
