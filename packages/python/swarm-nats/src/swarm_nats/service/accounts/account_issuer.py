from __future__ import annotations

# Standard library imports
import time
from logging import Logger, getLogger
from typing import ClassVar, Dict, List, Optional, cast
from uuid import UUID

# Third-party imports
from pydantic import JsonValue, SecretStr

# First-party imports
from swarm_nats.models.accounts.exceptions import SENatsJwtInvalidError
from swarm_nats.models.accounts.issued_account import IssuedAccount
from swarm_nats.models.accounts.issued_operator import IssuedOperator
from swarm_nats.models.enums import NatsClaimType
from swarm_nats.service.accounts.nats_jwt_signer import NatsJwtSigner
from swarm_nats.service.accounts.nkey_factory import NkeyFactory


class AccountIssuer:
    """Issue the NATS account of an Operator, and revoke users of it.

    Attributes:
        SUB_KEY (str): The claim key of the subject, the public key the token is about.
        ISS_KEY (str): The claim key of the issuer.
        NAME_KEY (str): The claim key of the name.
        NATS_KEY (str): The claim key of the NATS section.
        TYPE_KEY (str): The key of the claim type in the NATS section.
        VERSION_KEY (str): The key of the claim version in the NATS section.
        LIMITS_KEY (str): The key of the limits in the NATS section.
        REVOCATIONS_KEY (str): The key of the revoked users in the NATS section.
        NATS_VERSION (int): The version of the NATS JWT claims, 2.
        ACCOUNT_LIMITS (Dict[str, JsonValue]): The limits of an account. Copied before use.
        nkeys (NkeyFactory): Creates and restores the keys.
        signer (NatsJwtSigner): Signs and decodes the tokens.
        logger (Logger): Logger instance.

    Notes:
        - The account is named after the identifier of its Operator, so that one Operator has one account and the
          account is the boundary of its subjects (BR-008).
        - **The limits are all unlimited (-1), JetStream included** (``mem_storage`` and ``disk_storage``): the
          isolation comes from the account, not from a quota, and a quota is a later decision.
        - A revocation is a map from a user public key to a time in seconds: the server refuses every user JWT of
          that key issued at or before that time.
        - **Seeds are secrets: they are never logged.**
    """

    SUB_KEY: ClassVar[str] = "sub"
    ISS_KEY: ClassVar[str] = "iss"
    NAME_KEY: ClassVar[str] = "name"
    NATS_KEY: ClassVar[str] = "nats"
    TYPE_KEY: ClassVar[str] = "type"
    VERSION_KEY: ClassVar[str] = "version"
    LIMITS_KEY: ClassVar[str] = "limits"
    REVOCATIONS_KEY: ClassVar[str] = "revocations"
    NATS_VERSION: ClassVar[int] = 2
    ACCOUNT_LIMITS: ClassVar[Dict[str, JsonValue]] = {
        "subs": -1,
        "data": -1,
        "payload": -1,
        "imports": -1,
        "exports": -1,
        "wildcards": True,
        "conn": -1,
        "leaf": -1,
        "mem_storage": -1,
        "disk_storage": -1,
    }

    def __init__(self, nkeys: NkeyFactory, signer: NatsJwtSigner, logger: Optional[Logger] = None) -> None:
        self.nkeys = nkeys
        self.signer = signer
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _claims(self, public_key: str, name: str, revocations: Dict[str, JsonValue]) -> Dict[str, JsonValue]:
        """Build the claims of an account.

        Args:
            public_key (str): The public key of the account.
            name (str): The name of the account.
            revocations (Dict[str, JsonValue]): The revoked users, a time per public key.

        Returns:
            Dict[str, JsonValue]: The claims, without issuer, issue time and identifier, which the signer adds.

        Notes:
            - The ``revocations`` key is left out when there is none, as the NATS tools do.
        """
        nats: Dict[str, JsonValue] = {
            self.LIMITS_KEY: dict(self.ACCOUNT_LIMITS),
            self.TYPE_KEY: NatsClaimType.ACCOUNT.value,
            self.VERSION_KEY: self.NATS_VERSION,
        }
        if revocations:
            self.logger.debug("The account claims carry %d revocations.", len(revocations))
            nats[self.REVOCATIONS_KEY] = revocations
        else:
            self.logger.debug("The account claims carry no revocation.")
        return {self.SUB_KEY: public_key, self.NAME_KEY: name, self.NATS_KEY: nats}

    ############################
    # Publicly Exposed Methods #
    ############################

    def issue(self, operator: IssuedOperator, operator_id: UUID) -> IssuedAccount:
        """Issue the account of one Operator.

        Args:
            operator (IssuedOperator): The NATS operator that signs the account.
            operator_id (UUID): The identifier of the Operator, which names the account.

        Returns:
            IssuedAccount: The account, with its signed JWT.
        """
        account_key = self.nkeys.create(NatsClaimType.ACCOUNT)
        operator_key = self.nkeys.from_seed(operator.seed.get_secret_value())
        public_key = self.nkeys.public_key(account_key)
        name = str(operator_id)
        claims = self._claims(public_key, name, {})
        account = IssuedAccount(
            name=name,
            public_key=public_key,
            jwt=self.signer.sign(claims, operator_key),
            seed=SecretStr(self.nkeys.seed(account_key)),
        )
        self.logger.info("Issued account %s with public key %s.", account.name, account.public_key)
        return account

    def revoke(self, operator: IssuedOperator, account: IssuedAccount, user_public_keys: List[str]) -> IssuedAccount:
        """Revoke users of an account, by signing the account again with the operator key.

        Args:
            operator (IssuedOperator): The NATS operator that signed the account.
            account (IssuedAccount): The account, with its current JWT.
            user_public_keys (List[str]): The public keys of the users to revoke.

        Returns:
            IssuedAccount: The same account, with the same keys and a new JWT that holds every revocation.

        Raises:
            SENatsJwtInvalidError: When the JWT of the account was not issued by the operator.

        Notes:
            - The existing revocations are kept, and a key that is already revoked gets the current time.
            - **The new JWT is signed by the operator key, never the account key**: the server accepts an account JWT only from its operator, and the account keeps its own public key and seed.
        """
        current = self.signer.decode(account.jwt)
        if current.get(self.ISS_KEY) != operator.public_key:
            self.logger.error("Account %s was not issued by operator %s.", account.name, operator.public_key)
            raise SENatsJwtInvalidError(
                f"Invalid account JWT: {account.name}. Must be issued by operator {operator.public_key}."
            )
        nats = cast(Dict[str, JsonValue], current.get(self.NATS_KEY, {}))
        existing = nats.get(self.REVOCATIONS_KEY)
        revocations: Dict[str, JsonValue] = {}
        if isinstance(existing, dict):
            self.logger.debug("Kept %d existing revocations.", len(existing))
            revocations.update(existing)
        else:
            self.logger.debug("The account had no revocation.")
        now = int(time.time())
        for public_key in user_public_keys:
            self.logger.debug("Revoking user %s at %d.", public_key, now)
            revocations[public_key] = now
        operator_key = self.nkeys.from_seed(operator.seed.get_secret_value())
        claims = self._claims(account.public_key, account.name, revocations)
        revoked = IssuedAccount(
            name=account.name,
            public_key=account.public_key,
            jwt=self.signer.sign(claims, operator_key),
            seed=account.seed,
        )
        self.logger.info("Revoked %d users of account %s.", len(user_public_keys), account.name)
        return revoked
