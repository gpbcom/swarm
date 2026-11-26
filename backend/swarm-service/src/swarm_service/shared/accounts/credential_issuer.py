from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Dict, List, Optional
from uuid import UUID

# Third-party imports
from pydantic import JsonValue, SecretStr

# First-party imports
from swarm_models.accounts.exceptions import (
    SECredentialIssuerAccountMismatchError,
    SECredentialIssuerInvalidKindError,
)
from swarm_models.accounts.issued_account import IssuedAccount
from swarm_models.accounts.issued_credential import IssuedCredential
from swarm_models.accounts.issued_operator import IssuedOperator
from swarm_models.enums import CredentialKind, NatsClaimType
from swarm_models.subjects.operator_subjects import OperatorSubjects
from swarm_service.shared.accounts.nats_jwt_signer import NatsJwtSigner
from swarm_service.shared.accounts.nkey_factory import NkeyFactory


class CredentialIssuer:
    """Issue the NATS user credentials of an Operator, and of the system account.

    Attributes:
        SUB_KEY (str): The claim key of the subject, the public key the token is about.
        NAME_KEY (str): The claim key of the name.
        NATS_KEY (str): The claim key of the NATS section.
        TYPE_KEY (str): The key of the claim type in the NATS section.
        VERSION_KEY (str): The key of the claim version in the NATS section.
        PUB_KEY (str): The key of the publish permissions in the NATS section.
        SUBSCRIBE_KEY (str): The key of the subscribe permissions in the NATS section.
        ALLOW_KEY (str): The key of the allowed subjects of a permission.
        TAGS_KEY (str): The key of the tags in the NATS section.
        NATS_VERSION (int): The version of the NATS JWT claims, 2.
        MECHANISM_SUBJECTS (List[str]): The subjects the NATS machinery needs, which stay inside the account.
        USER_LIMITS (Dict[str, JsonValue]): The limits of a user, all unlimited. Copied before use.
        CREDS_TEMPLATE (str): The text of a creds file, with ``{jwt}`` and ``{seed}`` to fill in.
        nkeys (NkeyFactory): Creates and restores the keys.
        signer (NatsJwtSigner): Signs the tokens.
        logger (Logger): Logger instance.

    Notes:
        - A credential of an Operator may only publish and subscribe on its own ``op.<operator_id>.>`` subjects (BR-008)
          and on ``MECHANISM_SUBJECTS``.
        - **The mechanism subjects are ``_INBOX.>`` for replies, ``$JS.>`` for JetStream, ``$KV.>`` for the key
          value stores and ``$JSC.>`` for the JetStream cross-domain traffic.** A subject of an account is not visible to another account, so they keep the isolation. They
          are never ``>``, and never the subject of another Operator.
        - ``$JSC.>`` was added because, with it missing, a stream of the core that sources a stream of a leaf node
          (an edge) received nothing: the real server drops the source traffic that crosses the leaf link.
        - Simulated credentials are ordinary user credentials with their own key, tagged ``simulated`` (BR-014).
        - The system credential has no permission section, so it is unrestricted inside the system account.
        - **Seeds and JWTs are secrets: they are never logged.**
    """

    SUB_KEY: ClassVar[str] = "sub"
    NAME_KEY: ClassVar[str] = "name"
    NATS_KEY: ClassVar[str] = "nats"
    TYPE_KEY: ClassVar[str] = "type"
    VERSION_KEY: ClassVar[str] = "version"
    PUB_KEY: ClassVar[str] = "pub"
    SUBSCRIBE_KEY: ClassVar[str] = "sub"
    ALLOW_KEY: ClassVar[str] = "allow"
    TAGS_KEY: ClassVar[str] = "tags"
    NATS_VERSION: ClassVar[int] = 2
    MECHANISM_SUBJECTS: ClassVar[List[str]] = ["_INBOX.>", "$JS.>", "$KV.>", "$JSC.>"]
    USER_LIMITS: ClassVar[Dict[str, JsonValue]] = {"subs": -1, "data": -1, "payload": -1}
    CREDS_TEMPLATE: ClassVar[str] = (
        "-----BEGIN NATS USER JWT-----\n"
        "{jwt}\n"
        "------END NATS USER JWT------\n"
        "\n"
        "************************* IMPORTANT *************************\n"
        "    NKEY Seed printed below can be used to sign and prove identity.\n"
        "    NKEYs are sensitive and should be treated as secrets.\n"
        "\n"
        "-----BEGIN USER NKEY SEED-----\n"
        "{seed}\n"
        "------END USER NKEY SEED------\n"
        "\n"
        "*************************************************************\n"
    )

    def __init__(self, nkeys: NkeyFactory, signer: NatsJwtSigner, logger: Optional[Logger] = None) -> None:
        self.nkeys = nkeys
        self.signer = signer
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _claims(self, public_key: str, name: str, tag: str, subjects: Optional[List[str]]) -> Dict[str, JsonValue]:
        """Build the claims of a user.

        Args:
            public_key (str): The public key of the user.
            name (str): The name of the user.
            tag (str): The only tag of the user, its kind.
            subjects (Optional[List[str]]): The subjects it may publish and subscribe on, ``None`` for no restriction.

        Returns:
            Dict[str, JsonValue]: The claims, without issuer, issue time and identifier, which the signer adds.
        """
        nats: Dict[str, JsonValue] = dict(self.USER_LIMITS)
        nats[self.TYPE_KEY] = NatsClaimType.USER.value
        nats[self.VERSION_KEY] = self.NATS_VERSION
        nats[self.TAGS_KEY] = [tag]
        if subjects is None:
            self.logger.debug("The user %s has no subject restriction.", name)
        else:
            self.logger.debug("The user %s may use %d subjects.", name, len(subjects))
            allowed: List[JsonValue] = list(subjects)
            nats[self.PUB_KEY] = {self.ALLOW_KEY: allowed}
            nats[self.SUBSCRIBE_KEY] = {self.ALLOW_KEY: list(allowed)}
        return {self.SUB_KEY: public_key, self.NAME_KEY: name, self.NATS_KEY: nats}

    def _sign(
        self,
        issuer_seed: str,
        operator_id: Optional[UUID],
        kind: CredentialKind,
        name: str,
        subjects: Optional[List[str]],
    ) -> IssuedCredential:
        """Create a user key and sign its JWT.

        Args:
            issuer_seed (str): The seed of the account that signs.
            operator_id (Optional[UUID]): The Operator of the credential, ``None`` for the system account.
            kind (CredentialKind): The kind of the credential.
            name (str): The name of the identity.
            subjects (Optional[List[str]]): The allowed subjects, ``None`` for no restriction.

        Returns:
            IssuedCredential: The credential.
        """
        issuer_key = self.nkeys.from_seed(issuer_seed)
        user_key = self.nkeys.create(NatsClaimType.USER)
        public_key = self.nkeys.public_key(user_key)
        claims = self._claims(public_key, name, kind.value, subjects)
        credential = IssuedCredential(
            operator_id=operator_id,
            kind=kind,
            name=name,
            public_key=public_key,
            jwt=self.signer.sign(claims, issuer_key),
            seed=SecretStr(self.nkeys.seed(user_key)),
        )
        self.logger.info("Issued %s credential %s with public key %s.", kind.value, name, public_key)
        return credential

    ############################
    # Publicly Exposed Methods #
    ############################

    def issue(self, account: IssuedAccount, operator_id: UUID, kind: CredentialKind, name: str) -> IssuedCredential:
        """Issue a credential that is confined to the subjects of one Operator.

        Args:
            account (IssuedAccount): The account of the Operator, which signs.
            operator_id (UUID): The identifier of the Operator.
            kind (CredentialKind): The kind of identity: a service, an edge node or a simulated one.
            name (str): The name of the identity.

        Returns:
            IssuedCredential: The credential, with its signed JWT.

        Raises:
            SECredentialIssuerInvalidKindError: When the kind is ``SYSTEM``.
            SECredentialIssuerAccountMismatchError: When the account is not the account of the Operator.
        """
        if kind == CredentialKind.SYSTEM:
            self.logger.error("A credential of kind %s was requested for an Operator.", kind.value)
            raise SECredentialIssuerInvalidKindError(
                f"Invalid kind: {kind.value!r}. Must not be the system kind for an Operator credential."
            )
        if account.name != str(operator_id):
            self.logger.error("Account %s is not the account of Operator %s.", account.name, operator_id)
            raise SECredentialIssuerAccountMismatchError(
                f"Invalid account: {account.name!r}. Must be named {str(operator_id)!r}."
            )
        self.logger.debug("Checked the account and the kind of a credential for Operator %s.", operator_id)
        subjects = [OperatorSubjects(operator_id=operator_id).all(), *self.MECHANISM_SUBJECTS]
        return self._sign(account.seed.get_secret_value(), operator_id, kind, name, subjects)

    def issue_system(self, operator: IssuedOperator, name: str) -> IssuedCredential:
        """Issue a credential of the system account, with no subject restriction.

        Args:
            operator (IssuedOperator): The NATS operator, whose system account signs.
            name (str): The name of the identity.

        Returns:
            IssuedCredential: The credential, of kind ``SYSTEM`` and with no Operator.
        """
        return self._sign(operator.system_account.seed.get_secret_value(), None, CredentialKind.SYSTEM, name, None)

    def creds_file(self, credential: IssuedCredential) -> str:
        """Render the standard NATS creds file of a credential.

        Args:
            credential (IssuedCredential): The credential.

        Returns:
            str: The JWT block, the warning lines, then the seed block.

        Notes:
            - **The text holds the seed: the caller writes it with restricted rights and never logs it.**
        """
        self.logger.debug("Rendered the creds file of %s.", credential.name)
        return self.CREDS_TEMPLATE.format(jwt=credential.jwt, seed=credential.seed.get_secret_value())
