from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Dict, List, Optional

# Third-party imports
import jwt
from jwt.types import Options
from pydantic import JsonValue, ValidationError

# First-party imports
from gateway.clients.keycloak.keycloak_jwks_client import KeycloakJwksClient
from gateway.models.access.exceptions import (
    SEAccessExpiredTokenError,
    SEAccessInvalidTokenError,
    SEAccessMissingTokenError,
)
from gateway.models.auth.auth_config import AuthConfig
from gateway.models.auth.caller import Caller
from gateway.models.auth.exceptions import SEInvalidCallerException
from gateway.models.enums import TokenClaim
from gateway.models.keycloak.exceptions import SEKeycloakUnknownKeyError
from swarm_models.people.enums import RoleName


class TokenVerifier:
    """Checks a bearer token and gives the caller it names.

    Attributes:
        config (AuthConfig): The configuration of the check of the tokens.
        keys (KeycloakJwksClient): Where the signing keys come from.
        logger (Logger): Logger instance.
        ALGORITHM (str): The only signing algorithm accepted.
        KID_HEADER (str): The name of the key identifier in the token header.
        DECODE_OPTIONS (Options): The decode options, which require the expiry, issue time and subject claims.

    Notes:
        - **Neither the token nor any claim value is ever logged**: only the type of the error and the refusal.
        - An unreachable identity provider is not a refusal, so ``SEKeycloakUnreachableError`` goes up unchanged.
        - Only the algorithm ``RS256`` is accepted, which refuses ``none`` and symmetric keys.
    """

    ALGORITHM: ClassVar[str] = "RS256"
    KID_HEADER: ClassVar[str] = "kid"
    DECODE_OPTIONS: ClassVar[Options] = {
        "require": [TokenClaim.EXPIRES_AT.value, TokenClaim.ISSUED_AT.value, TokenClaim.SUBJECT.value]
    }

    def __init__(self, config: AuthConfig, keys: KeycloakJwksClient, logger: Optional[Logger] = None) -> None:
        """Prepare a verifier.

        Args:
            config (AuthConfig): The configuration of the check of the tokens.
            keys (KeycloakJwksClient): Where the signing keys come from.
            logger (Optional[Logger]): Logger instance.
        """
        self.config = config
        self.keys = keys
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _key_id(self, token: str) -> str:
        """Read the key identifier from the unverified header.

        Args:
            token (str): The bearer token.

        Returns:
            str: The ``kid`` of the header.

        Raises:
            SEAccessInvalidTokenError: If the header cannot be read or holds no key identifier.
        """
        try:
            header = jwt.get_unverified_header(token)
        except jwt.InvalidTokenError as error:
            self.logger.error("The token header is unreadable: %s.", type(error).__name__)
            raise SEAccessInvalidTokenError("The token is invalid.") from error
        key_id = header.get(self.KID_HEADER)
        if not isinstance(key_id, str) or not key_id:
            self.logger.error("The token header names no signing key.")
            raise SEAccessInvalidTokenError("The token is invalid.")
        self.logger.debug("The token header names a signing key.")
        return key_id

    def _claims(self, token: str, key: jwt.PyJWK) -> Dict[str, JsonValue]:
        """Check the signature and the claims of a token.

        Args:
            token (str): The bearer token.
            key (jwt.PyJWK): The signing key.

        Returns:
            Dict[str, JsonValue]: The claims.

        Raises:
            SEAccessExpiredTokenError: If the token is past its expiry.
            SEAccessInvalidTokenError: If the signature or a claim is wrong.
        """
        try:
            claims: Dict[str, JsonValue] = jwt.decode(
                token,
                key,
                algorithms=[self.ALGORITHM],
                issuer=self.config.issuer_url,
                audience=self.config.audience,
                leeway=self.config.leeway_s,
                options=self.DECODE_OPTIONS,
            )
        except jwt.ExpiredSignatureError as error:
            self.logger.error("The token is expired: %s.", type(error).__name__)
            raise SEAccessExpiredTokenError("The token is expired.") from error
        except jwt.InvalidTokenError as error:
            self.logger.error("The token is refused: %s.", type(error).__name__)
            raise SEAccessInvalidTokenError("The token is invalid.") from error
        self.logger.debug("The token signature and claims are valid.")
        return claims

    def _roles(self, claims: Dict[str, JsonValue]) -> List[str]:
        """Keep the Swarm roles of the realm access section.

        Args:
            claims (Dict[str, JsonValue]): The claims of the token.

        Returns:
            List[str]: The role names that Swarm knows, in their order.
        """
        realm_access = claims.get(TokenClaim.REALM_ACCESS.value)
        if not isinstance(realm_access, dict):
            self.logger.debug("The token has no realm access section.")
            return []
        raw_roles = realm_access.get(TokenClaim.ROLES.value)
        if not isinstance(raw_roles, list):
            self.logger.debug("The token has no list of roles.")
            return []
        known = {role.value for role in RoleName}
        roles = [role for role in raw_roles if isinstance(role, str) and role in known]
        self.logger.debug("Kept %d of %d roles.", len(roles), len(raw_roles))
        return roles

    ############################
    # Publicly Exposed Methods #
    ############################

    async def verify(self, token: Optional[str]) -> Caller:
        """Check a bearer token and give the caller it names.

        Args:
            token (Optional[str]): The bearer token, without its scheme.

        Returns:
            Caller: The person, Operator and roles of the token.

        Raises:
            SEAccessMissingTokenError: If there is no token.
            SEAccessExpiredTokenError: If the token is past its expiry.
            SEAccessInvalidTokenError: If the token is malformed, wrongly signed, or names an invalid caller.
            SEKeycloakUnreachableError: If the identity provider cannot be reached.
        """
        if token is None or not token.strip():
            self.logger.error("The call carries no token.")
            raise SEAccessMissingTokenError("The call carries no token.")
        token = token.strip()
        key_id = self._key_id(token)
        try:
            jwk = await self.keys.signing_key(key_id)
        except SEKeycloakUnknownKeyError as error:
            self.logger.error("The signing key of the token is unknown: %s.", type(error).__name__)
            raise SEAccessInvalidTokenError("The token is invalid.") from error
        try:
            key = jwt.PyJWK(jwk)
        except jwt.PyJWTError as error:
            self.logger.error("The signing key is unusable: %s.", type(error).__name__)
            raise SEAccessInvalidTokenError("The token is invalid.") from error
        claims = self._claims(token, key)
        try:
            caller = Caller.model_validate(
                {
                    Caller.PERSON_ID_FIELD: claims.get(TokenClaim.SUBJECT.value),
                    Caller.OPERATOR_ID_FIELD: claims.get(TokenClaim.OPERATOR_ID.value),
                    Caller.ROLES_FIELD: self._roles(claims),
                }
            )
        except (SEInvalidCallerException, ValidationError) as error:
            self.logger.error("The claims do not make a caller: %s.", type(error).__name__)
            raise SEAccessInvalidTokenError("The token is invalid.") from error
        self.logger.info("Verified a token.")
        return caller
