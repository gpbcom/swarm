from __future__ import annotations

# Standard library imports
import base64
import binascii
import hashlib
import json
import time
from logging import Logger, getLogger
from typing import ClassVar, Dict, List, Optional, Tuple, Union

# Third-party imports
import nkeys  # type: ignore[import-untyped]
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from nkeys import KeyPair  # type: ignore[import-untyped]
from pydantic import JsonValue

# First-party imports
from swarm_nats.models.accounts.exceptions import SENatsJwtInvalidError


class NatsJwtSigner:
    """Sign claims into NATS JWTs and check them.

    Attributes:
        TYP_KEY (str): The header key of the token type.
        ALG_KEY (str): The header key of the algorithm.
        TYP_VALUE (str): The token type, ``JWT``.
        ALG_VALUE (str): The algorithm, ``ed25519-nkey``.
        HEADER (Dict[str, str]): The header of every token. Copied before use.
        IAT_KEY (str): The claim key of the issue time.
        ISS_KEY (str): The claim key of the issuer.
        JTI_KEY (str): The claim key of the identifier.
        SEPARATOR (str): The separator of the three parts of a token.
        PADDING (str): The base64 and base32 padding character.
        ENCODING (str): The encoding of text.
        JSON_SEPARATORS (Tuple[str, str]): The separators of compact JSON.
        PART_COUNT (int): The number of parts of a token.
        PUBLIC_KEY_PREFIX_LENGTH (int): The length in bytes of the role prefix of a public key.
        PUBLIC_KEY_LENGTH (int): The length in bytes of a raw ed25519 public key.
        CRC_LENGTH (int): The length in bytes of the CRC16 of a public key.
        BASE32_BLOCK (int): The size of a padded base32 block.
        BASE64_BLOCK (int): The size of a padded base64 block.
        logger (Logger): Logger instance.

    Notes:
        - A NATS JWT is ``header.payload.signature``. Each part is base64url without padding.
        - The header is ``{"typ": "JWT", "alg": "ed25519-nkey"}``, and the payload is the claims as compact JSON.
        - The signature is the ed25519 signature of ``header.payload`` by the issuer, and ``iss`` is the issuer's
          public key, so a token carries what is needed to check it.
        - ``jti`` is the base32 SHA-256 of the claims serialised without ``jti``.
        - Verification uses PyNaCl with the public key decoded from ``iss``, because ``nkeys.KeyPair`` can only verify
          when it holds a seed. The CRC16 and the role prefix of the public key are checked with ``nkeys``.
        - **Tokens and seeds are never logged.**
    """

    TYP_KEY: ClassVar[str] = "typ"
    ALG_KEY: ClassVar[str] = "alg"
    TYP_VALUE: ClassVar[str] = "JWT"
    ALG_VALUE: ClassVar[str] = "ed25519-nkey"
    HEADER: ClassVar[Dict[str, str]] = {TYP_KEY: TYP_VALUE, ALG_KEY: ALG_VALUE}
    IAT_KEY: ClassVar[str] = "iat"
    ISS_KEY: ClassVar[str] = "iss"
    JTI_KEY: ClassVar[str] = "jti"
    SEPARATOR: ClassVar[str] = "."
    PADDING: ClassVar[str] = "="
    ENCODING: ClassVar[str] = "utf-8"
    JSON_SEPARATORS: ClassVar[Tuple[str, str]] = (",", ":")
    PART_COUNT: ClassVar[int] = 3
    PUBLIC_KEY_PREFIX_LENGTH: ClassVar[int] = 1
    PUBLIC_KEY_LENGTH: ClassVar[int] = 32
    CRC_LENGTH: ClassVar[int] = 2
    BASE32_BLOCK: ClassVar[int] = 8
    BASE64_BLOCK: ClassVar[int] = 4

    def __init__(self, logger: Optional[Logger] = None) -> None:
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _b64encode(self, raw: bytes) -> str:
        """Encode bytes as base64url without padding.

        Args:
            raw (bytes): The bytes.

        Returns:
            str: The text.
        """
        return base64.urlsafe_b64encode(raw).decode(self.ENCODING).rstrip(self.PADDING)

    def _b64decode(self, part: str) -> bytes:
        """Decode base64url text without padding.

        Args:
            part (str): The text.

        Returns:
            bytes: The bytes.
        """
        padded = part + self.PADDING * (-len(part) % self.BASE64_BLOCK)
        return base64.urlsafe_b64decode(padded.encode(self.ENCODING))

    def _dump(self, value: Union[Dict[str, JsonValue], Dict[str, str]]) -> bytes:
        """Serialise a mapping as compact JSON.

        Args:
            value (Union[Dict[str, JsonValue], Dict[str, str]]): The mapping.

        Returns:
            bytes: The JSON.
        """
        return json.dumps(value, separators=self.JSON_SEPARATORS).encode(self.ENCODING)

    def _identifier(self, claims: Dict[str, JsonValue]) -> str:
        """Compute the ``jti`` of claims that have none.

        Args:
            claims (Dict[str, JsonValue]): The claims, without ``jti``.

        Returns:
            str: The base32 SHA-256 of their compact JSON, without padding.
        """
        digest = hashlib.sha256(self._dump(claims)).digest()
        return base64.b32encode(digest).decode(self.ENCODING).rstrip(self.PADDING)

    def _refuse(self, reason: str) -> SENatsJwtInvalidError:
        """Log a refusal and build its error.

        Args:
            reason (str): Why the token is refused.

        Returns:
            SENatsJwtInvalidError: The error to raise.
        """
        self.logger.error("A token was refused: %s", reason)
        return SENatsJwtInvalidError(f"Invalid token: {reason} Must be a signed NATS JWT.")

    def _verify_key(self, issuer: str) -> VerifyKey:
        """Build the verification key of an issuer's public key.

        Args:
            issuer (str): The public key, as written in ``iss``.

        Returns:
            VerifyKey: The key that checks its signatures.

        Raises:
            SENatsJwtInvalidError: When the public key is malformed or its CRC16 or role is wrong.
        """
        padded = issuer + self.PADDING * (-len(issuer) % self.BASE32_BLOCK)
        try:
            raw = base64.b32decode(padded.encode(self.ENCODING))
        except (binascii.Error, ValueError) as error:
            raise self._refuse("the issuer is not base32.") from error
        body = raw[: -self.CRC_LENGTH]
        crc = raw[-self.CRC_LENGTH :]
        if len(body) != self.PUBLIC_KEY_PREFIX_LENGTH + self.PUBLIC_KEY_LENGTH:
            raise self._refuse("the issuer has the wrong length.")
        if nkeys.crc16_checksum(body) != crc:
            raise self._refuse("the issuer has a wrong checksum.")
        if not nkeys.valid_public_prefix_byte(body[0]):
            raise self._refuse("the issuer has an unknown role.")
        self.logger.debug("Built the verification key of an issuer.")
        return VerifyKey(body[self.PUBLIC_KEY_PREFIX_LENGTH :])

    ############################
    # Publicly Exposed Methods #
    ############################

    def sign(self, claims: Dict[str, JsonValue], issuer: KeyPair) -> str:
        """Sign claims into a token.

        Args:
            claims (Dict[str, JsonValue]): The claims. They are copied, never changed.
            issuer (KeyPair): The key pair that signs, an operator or an account.

        Returns:
            str: The compact token.
        """
        issuer_public_key = bytes(issuer.public_key).decode(self.ENCODING)
        payload_claims = dict(claims)
        payload_claims[self.IAT_KEY] = int(time.time())
        payload_claims[self.ISS_KEY] = issuer_public_key
        payload_claims.pop(self.JTI_KEY, None)
        payload_claims[self.JTI_KEY] = self._identifier(payload_claims)
        header = self._b64encode(self._dump(dict(self.HEADER)))
        payload = self._b64encode(self._dump(payload_claims))
        signing_input = f"{header}{self.SEPARATOR}{payload}"
        signature = self._b64encode(issuer.sign(signing_input.encode(self.ENCODING)))
        self.logger.debug("Signed a token for issuer %s.", issuer_public_key)
        return f"{signing_input}{self.SEPARATOR}{signature}"

    def decode(self, token: str) -> Dict[str, JsonValue]:
        """Check a token and give its claims.

        Args:
            token (str): The compact token.

        Returns:
            Dict[str, JsonValue]: The claims, once the header and the signature are checked.

        Raises:
            SENatsJwtInvalidError: When the token is malformed or its signature does not match its issuer.
        """
        parts: List[str] = token.split(self.SEPARATOR)
        if len(parts) != self.PART_COUNT:
            raise self._refuse(f"it has {len(parts)} parts.")
        header_part, payload_part, signature_part = parts
        try:
            header = json.loads(self._b64decode(header_part))
            claims = json.loads(self._b64decode(payload_part))
            signature = self._b64decode(signature_part)
        except (ValueError, binascii.Error) as error:
            raise self._refuse("a part cannot be decoded.") from error
        if header != self.HEADER:
            raise self._refuse("the header is not an ed25519-nkey JWT header.")
        if not isinstance(claims, dict):
            raise self._refuse("the claims are not a JSON object.")
        issuer = claims.get(self.ISS_KEY)
        if not isinstance(issuer, str):
            raise self._refuse("the issuer is missing.")
        signing_input = f"{header_part}{self.SEPARATOR}{payload_part}".encode(self.ENCODING)
        try:
            self._verify_key(issuer).verify(signing_input, signature)
        except BadSignatureError as error:
            raise self._refuse("the signature does not match its issuer.") from error
        self.logger.debug("Checked a token of issuer %s.", issuer)
        return claims
