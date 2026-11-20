from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Dict, Optional

# Third-party imports
from pydantic import JsonValue, SecretStr

# First-party imports
from swarm_nats.models.accounts.issued_account import IssuedAccount
from swarm_nats.models.accounts.issued_operator import IssuedOperator
from swarm_nats.models.enums import NatsClaimType
from swarm_nats.service.accounts.nats_jwt_signer import NatsJwtSigner
from swarm_nats.service.accounts.nkey_factory import NkeyFactory


class OperatorIssuer:
    """Issue the NATS operator and its system account.

    Attributes:
        SUB_KEY (str): The claim key of the subject, the public key the token is about.
        NAME_KEY (str): The claim key of the name.
        NATS_KEY (str): The claim key of the NATS section.
        TYPE_KEY (str): The key of the claim type in the NATS section.
        VERSION_KEY (str): The key of the claim version in the NATS section.
        SYSTEM_ACCOUNT_KEY (str): The key of the system account in the NATS section of an operator.
        LIMITS_KEY (str): The key of the limits in the NATS section of an account.
        NATS_VERSION (int): The version of the NATS JWT claims, 2.
        SYSTEM_ACCOUNT_NAME (str): The name of the system account, ``SYS``.
        SYSTEM_LIMITS (Dict[str, JsonValue]): The limits of the system account, with no JetStream. Copied before use.
        nkeys (NkeyFactory): Creates the keys.
        signer (NatsJwtSigner): Signs the tokens.
        logger (Logger): Logger instance.

    Notes:
        - An operator JWT is self-signed: its subject and its issuer are the operator key.
        - The system account JWT is signed by the operator key, and the operator JWT names the system account in
          ``nats.system_account``, which is how the server knows which account may see every other account.
        - The system account has no JetStream limit, so it has no JetStream.
        - **Seeds are secrets: they are never logged.**
    """

    SUB_KEY: ClassVar[str] = "sub"
    NAME_KEY: ClassVar[str] = "name"
    NATS_KEY: ClassVar[str] = "nats"
    TYPE_KEY: ClassVar[str] = "type"
    VERSION_KEY: ClassVar[str] = "version"
    SYSTEM_ACCOUNT_KEY: ClassVar[str] = "system_account"
    LIMITS_KEY: ClassVar[str] = "limits"
    NATS_VERSION: ClassVar[int] = 2
    SYSTEM_ACCOUNT_NAME: ClassVar[str] = "SYS"
    SYSTEM_LIMITS: ClassVar[Dict[str, JsonValue]] = {
        "subs": -1,
        "data": -1,
        "payload": -1,
        "imports": -1,
        "exports": -1,
        "wildcards": True,
        "conn": -1,
        "leaf": -1,
    }

    def __init__(self, nkeys: NkeyFactory, signer: NatsJwtSigner, logger: Optional[Logger] = None) -> None:
        self.nkeys = nkeys
        self.signer = signer
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def issue(self, name: str) -> IssuedOperator:
        """Issue an operator and its system account.

        Args:
            name (str): The name of the operator.

        Returns:
            IssuedOperator: The operator, with its signed JWT and its system account.

        Raises:
            SEIssuedOperatorInvalidName: When the name is empty.
        """
        operator_key = self.nkeys.create(NatsClaimType.OPERATOR)
        system_key = self.nkeys.create(NatsClaimType.ACCOUNT)
        operator_public_key = self.nkeys.public_key(operator_key)
        system_public_key = self.nkeys.public_key(system_key)
        system_claims: Dict[str, JsonValue] = {
            self.SUB_KEY: system_public_key,
            self.NAME_KEY: self.SYSTEM_ACCOUNT_NAME,
            self.NATS_KEY: {
                self.LIMITS_KEY: dict(self.SYSTEM_LIMITS),
                self.TYPE_KEY: NatsClaimType.ACCOUNT.value,
                self.VERSION_KEY: self.NATS_VERSION,
            },
        }
        system_account = IssuedAccount(
            name=self.SYSTEM_ACCOUNT_NAME,
            public_key=system_public_key,
            jwt=self.signer.sign(system_claims, operator_key),
            seed=SecretStr(self.nkeys.seed(system_key)),
        )
        operator_claims: Dict[str, JsonValue] = {
            self.SUB_KEY: operator_public_key,
            self.NAME_KEY: name,
            self.NATS_KEY: {
                self.SYSTEM_ACCOUNT_KEY: system_public_key,
                self.TYPE_KEY: NatsClaimType.OPERATOR.value,
                self.VERSION_KEY: self.NATS_VERSION,
            },
        }
        operator = IssuedOperator(
            name=name,
            public_key=operator_public_key,
            jwt=self.signer.sign(operator_claims, operator_key),
            seed=SecretStr(self.nkeys.seed(operator_key)),
            system_account=system_account,
        )
        self.logger.info("Issued operator %s with public key %s.", operator.name, operator.public_key)
        return operator
