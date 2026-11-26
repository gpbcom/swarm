from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from time import monotonic
from typing import ClassVar, Dict, List, Optional

# Third-party imports
import httpx
from pydantic import JsonValue

# First-party imports
from gateway.models.auth.auth_config import AuthConfig
from gateway.models.keycloak.exceptions import SEKeycloakUnknownKeyError, SEKeycloakUnreachableError


class KeycloakJwksClient:
    """Fetches and caches the signing keys of the identity provider.

    Attributes:
        config (AuthConfig): The configuration of the check of the tokens.
        logger (Logger): Logger instance.
        signing_keys (Dict[str, Dict[str, JsonValue]]): The cached keys, by key identifier.
        expires_at (float): The monotonic time at which the cached keys expire.
        CERTS_PATH (str): The path of the key set, below the issuer URL.
        KEYS_FIELD (str): The name of the list of keys in the key set.
        KID_FIELD (str): The name of the identifier of a key.

    Notes:
        - A short-lived HTTP client is made for each fetch, so that nothing stays open.
        - **An unknown key identifier refetches once** when the cache is still valid, in case the keys rotated.
        - This is a short request, so it is not an ``AsyncRunnable``.
    """

    CERTS_PATH: ClassVar[str] = "/protocol/openid-connect/certs"
    KEYS_FIELD: ClassVar[str] = "keys"
    KID_FIELD: ClassVar[str] = "kid"

    def __init__(self, config: AuthConfig, logger: Optional[Logger] = None) -> None:
        self.config = config
        self.logger = logger if logger else getLogger(__name__)
        self.signing_keys: Dict[str, Dict[str, JsonValue]] = {}
        self.expires_at = 0.0

    ############################
    # Internal Helpers Methods #
    ############################

    def _cache_is_valid(self) -> bool:
        """Tell whether the cached keys are still within their lifetime.

        Returns:
            bool: True when the cache holds keys that have not expired.
        """
        return bool(self.signing_keys) and monotonic() < self.expires_at

    async def _fetch(self) -> None:
        """Fetch the key set and replace the cache with it.

        Raises:
            SEKeycloakUnreachableError: When the call fails or the key set is malformed.
        """
        url = f"{self.config.issuer_url}{self.CERTS_PATH}"
        try:
            async with httpx.AsyncClient(timeout=self.config.request_timeout_s) as http:
                response = await http.get(url)
            if response.status_code != httpx.codes.OK:
                raise ValueError(f"The identity provider answered {response.status_code}.")
            body = response.json()
            keys: List[Dict[str, JsonValue]] = body[self.KEYS_FIELD]
            fetched = {str(key[self.KID_FIELD]): key for key in keys}
        except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError) as error:
            self.logger.error("Could not fetch the signing keys: %s.", type(error).__name__)
            raise SEKeycloakUnreachableError("The signing keys could not be fetched.") from error
        self.signing_keys = fetched
        self.expires_at = monotonic() + self.config.jwks_cache_ttl_s
        self.logger.info("Fetched %d signing keys.", len(fetched))

    ############################
    # Publicly Exposed Methods #
    ############################

    async def signing_key(self, key_id: str) -> Dict[str, JsonValue]:
        """Return the signing key of an identifier.

        Args:
            key_id (str): The ``kid`` of the token header.

        Returns:
            Dict[str, JsonValue]: The key, as a JSON Web Key.

        Raises:
            SEKeycloakUnknownKeyError: When the identity provider does not serve this key.
            SEKeycloakUnreachableError: When the identity provider cannot be reached or answers badly.
        """
        if self._cache_is_valid():
            if key_id in self.signing_keys:
                self.logger.debug("Signing key %s found in the cache.", key_id)
                return self.signing_keys[key_id]
            self.logger.debug("Signing key %s not in the cache, fetching again.", key_id)
        else:
            self.logger.debug("The cache is empty or expired, fetching the keys.")
        await self._fetch()
        if key_id in self.signing_keys:
            return self.signing_keys[key_id]
        self.logger.error("Signing key %s is not served by the identity provider.", key_id)
        raise SEKeycloakUnknownKeyError(f"Unknown signing key: {key_id!r}.")
