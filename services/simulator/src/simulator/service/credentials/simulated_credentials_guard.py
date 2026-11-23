from __future__ import annotations

# Standard library imports
from base64 import urlsafe_b64decode
from json import loads
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, List, Optional

# Third-party imports
from pydantic import JsonValue

# First-party imports
from simulator.models.credentials.exceptions import (
    SESimulatedCredentialsNotSimulatedError,
    SESimulatedCredentialsUnreadableError,
)
from swarm_nats.models.enums import CredentialKind


class SimulatedCredentialsGuard:
    """Refuse any NATS credentials that are not tagged as simulated.

    Attributes:
        ENCODING (str): The encoding of a creds file.
        JWT_BEGIN (str): The line that opens the JWT block.
        JWT_END (str): The line that closes the JWT block.
        JWT_SEPARATOR (str): The separator of the parts of a JWT.
        PAYLOAD_INDEX (int): The index of the payload among the parts of a JWT.
        PADDING (str): The character that pads a base64 text.
        BASE64_BLOCK (int): The length multiple of a padded base64 text.
        NATS_KEY (str): The claim that holds the NATS section.
        TAGS_KEY (str): The field of the NATS section that holds the tags.
        logger (Logger): Logger instance.

    Notes:
        - **Nothing read from the file is ever logged: not the JWT, not the seed, not the claims.**
    """

    ENCODING: ClassVar[str] = "utf-8"
    JWT_BEGIN: ClassVar[str] = "-----BEGIN NATS USER JWT-----"
    JWT_END: ClassVar[str] = "------END NATS USER JWT------"
    JWT_SEPARATOR: ClassVar[str] = "."
    PAYLOAD_INDEX: ClassVar[int] = 1
    PADDING: ClassVar[str] = "="
    BASE64_BLOCK: ClassVar[int] = 4
    NATS_KEY: ClassVar[str] = "nats"
    TAGS_KEY: ClassVar[str] = "tags"

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Create the guard.

        Args:
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _unreadable(self, path: str, error: Exception) -> SESimulatedCredentialsUnreadableError:
        """Log and build the error of an unreadable credentials file.

        Args:
            path (str): The path of the creds file.
            error (Exception): The cause.

        Returns:
            SESimulatedCredentialsUnreadableError: The error to raise.
        """
        self.logger.error("Unreadable credentials %s: %s.", path, type(error).__name__)
        return SESimulatedCredentialsUnreadableError(f"Cannot read the credentials {path}: {type(error).__name__}.")

    def _jwt(self, text: str) -> str:
        """Find the JWT between the BEGIN and END lines.

        Args:
            text (str): The content of the creds file.

        Returns:
            str: The JWT.

        Raises:
            ValueError: When there is no JWT block.
        """
        lines: List[str] = [line.strip() for line in text.splitlines()]
        if self.JWT_BEGIN not in lines:
            self.logger.debug("No JWT block start line.")
            raise ValueError("No JWT block.")
        start = lines.index(self.JWT_BEGIN) + 1
        if self.JWT_END not in lines[start:]:
            self.logger.debug("No JWT block end line.")
            raise ValueError("No JWT block.")
        end = lines.index(self.JWT_END, start)
        jwt = "".join(lines[start:end])
        if not jwt:
            self.logger.debug("The JWT block is empty.")
            raise ValueError("Empty JWT block.")
        return jwt

    def _claims(self, jwt: str) -> JsonValue:
        """Decode the payload of a JWT.

        Args:
            jwt (str): The JWT.

        Returns:
            JsonValue: The parsed claims.

        Raises:
            ValueError: When the payload is missing, not base64url or not JSON.
        """
        parts = jwt.split(self.JWT_SEPARATOR)
        if len(parts) <= self.PAYLOAD_INDEX:
            self.logger.debug("The JWT has no payload.")
            raise ValueError("No payload.")
        payload = parts[self.PAYLOAD_INDEX]
        padded = payload + self.PADDING * (-len(payload) % self.BASE64_BLOCK)
        claims: JsonValue = loads(urlsafe_b64decode(padded.encode(self.ENCODING)).decode(self.ENCODING))
        return claims

    def _tags(self, claims: JsonValue) -> List[JsonValue]:
        """Read the tags of the claims.

        Args:
            claims (JsonValue): The parsed claims.

        Returns:
            List[JsonValue]: The tags, empty when there are none.
        """
        if not isinstance(claims, dict):
            self.logger.debug("The claims are not an object.")
            return []
        section = claims.get(self.NATS_KEY)
        if not isinstance(section, dict):
            self.logger.debug("The claims have no NATS section.")
            return []
        tags = section.get(self.TAGS_KEY)
        if not isinstance(tags, list):
            self.logger.debug("The NATS section has no tags.")
            return []
        return tags

    ############################
    # Publicly Exposed Methods #
    ############################

    def check(self, path: str) -> None:
        """Check that a creds file holds simulated credentials.

        Args:
            path (str): The path of the creds file.

        Raises:
            SESimulatedCredentialsUnreadableError: When the file or its JWT cannot be read.
            SESimulatedCredentialsNotSimulatedError: When the credentials are not tagged as simulated.
        """
        try:
            text = Path(path).read_text(encoding=self.ENCODING)
            claims = self._claims(self._jwt(text))
        except (OSError, ValueError) as error:
            raise self._unreadable(path, error) from error
        if CredentialKind.SIMULATED.value not in self._tags(claims):
            self.logger.error("The credentials %s are not simulated.", path)
            raise SESimulatedCredentialsNotSimulatedError(f"The credentials {path} are not tagged as simulated.")
        self.logger.info("Accepted the simulated credentials %s.", path)
