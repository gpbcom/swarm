from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import List, Optional
from uuid import UUID

# First-party imports
from gateway.clients.keycloak.keycloak_jwks_client import KeycloakJwksClient
from gateway.models.auth.auth_config import AuthConfig
from gateway.models.auth.caller import Caller
from gateway.service.auth.access_guard import AccessGuard
from gateway.service.auth.token_verifier import TokenVerifier
from swarm_models.people.enums import RoleName


class AccessService:
    """The access check that the api layer calls before it serves a call.

    Attributes:
        verifier (TokenVerifier): Checks the bearer token and gives the caller.
        guard (AccessGuard): Checks the Operator and the role of the call.
        logger (Logger): Logger instance.

    Notes:
        - **The token is never logged.**
        - Errors go up unchanged, because they were logged where they were raised.
    """

    def __init__(self, verifier: TokenVerifier, guard: AccessGuard, logger: Optional[Logger] = None) -> None:
        """Prepare the access check.

        Args:
            verifier (TokenVerifier): Checks the bearer token and gives the caller.
            guard (AccessGuard): Checks the Operator and the role of the call.
            logger (Optional[Logger]): Logger instance.
        """
        self.verifier = verifier
        self.guard = guard
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def from_config(cls, config: AuthConfig, logger: Optional[Logger] = None) -> AccessService:
        """Build the access check and everything it needs from the configuration.

        Args:
            config (AuthConfig): The configuration of the check of the tokens.
            logger (Optional[Logger]): Logger instance.

        Returns:
            AccessService: The access check.
        """
        client = KeycloakJwksClient(config)
        service = cls(TokenVerifier(config, client), AccessGuard())
        if logger:
            service.logger = logger
            service.logger.debug("Built the access check with the given logger.")
        else:
            service.logger.debug("Built the access check with its own logger.")
        return service

    async def authorise(self, token: Optional[str], roles: List[RoleName], operator_id: Optional[UUID]) -> Caller:
        """Check a token, then the Operator and the role of the call.

        Args:
            token (Optional[str]): The bearer token, without its scheme.
            roles (List[RoleName]): The roles that may make the call.
            operator_id (Optional[UUID]): The Operator the call names, none when it names no Operator.

        Returns:
            Caller: The verified caller.

        Raises:
            SEAccessMissingTokenError: If there is no token.
            SEAccessExpiredTokenError: If the token is expired.
            SEAccessInvalidTokenError: If the token is invalid.
            SEAccessWrongOperatorError: If the call names another Operator.
            SEAccessMissingRoleError: If the caller holds none of the roles.
            SEKeycloakUnreachableError: If the identity provider cannot be reached.
        """
        self.logger.debug("Authorising a call that needs one of %d roles.", len(roles))
        caller = await self.verifier.verify(token)
        self.guard.check(caller, roles, operator_id)
        self.logger.debug("The call is authorised.")
        return caller
