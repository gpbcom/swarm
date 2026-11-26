from __future__ import annotations

# Standard library imports
import json
import threading
import time
from http.server import ThreadingHTTPServer
from types import TracebackType
from typing import ClassVar, Dict, List, Optional, Self, Type
from uuid import uuid4

# Third-party imports
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm
from pydantic import JsonValue

# First-party imports
from services.gateway.tests.support.keycloak.certs_request_handler import CertsRequestHandler
from services.gateway.tests.support.keycloak.helpers import REALM_PATH


class KeycloakStandIn:
    """A local stand-in for Keycloak: serves its signing keys and signs real tokens.

    Attributes:
        HOST (str): The address the server listens on.
        ALGORITHM (str): The signing algorithm.
        KEY_ID_FIELD (str): The JWK field holding the key id.
        KEYS_FIELD (str): The JWKS field holding the keys.
        ISSUED_AT_CLAIM (str): The ``iat`` claim.
        EXPIRES_CLAIM (str): The ``exp`` claim.
        KEY_SIZE_BITS (int): The size of the RSA keys.
        PUBLIC_EXPONENT (int): The public exponent of the RSA keys.
        ENCODING (str): The encoding of the served body.
    """

    HOST: ClassVar[str] = "127.0.0.1"
    ALGORITHM: ClassVar[str] = "RS256"
    KEY_ID_FIELD: ClassVar[str] = "kid"
    KEYS_FIELD: ClassVar[str] = "keys"
    ISSUED_AT_CLAIM: ClassVar[str] = "iat"
    EXPIRES_CLAIM: ClassVar[str] = "exp"
    KEY_SIZE_BITS: ClassVar[int] = 2048
    PUBLIC_EXPONENT: ClassVar[int] = 65537
    ENCODING: ClassVar[str] = "utf-8"

    def __init__(self) -> None:
        self.key = self.new_key()
        self.key_id = uuid4().hex
        self.certs_count = 0
        self.server: Optional[ThreadingHTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    ############################
    # Internal Helpers Methods #
    ############################

    def new_key(self) -> rsa.RSAPrivateKey:
        return rsa.generate_private_key(public_exponent=self.PUBLIC_EXPONENT, key_size=self.KEY_SIZE_BITS)

    def sign(self, key: rsa.RSAPrivateKey, key_id: str, claims: Dict[str, JsonValue], expires_in_s: int) -> str:
        now = int(time.time())
        payload: Dict[str, JsonValue] = {
            **claims,
            self.ISSUED_AT_CLAIM: now,
            self.EXPIRES_CLAIM: now + expires_in_s,
        }
        pem = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        return jwt.encode(payload, pem, algorithm=self.ALGORITHM, headers={self.KEY_ID_FIELD: key_id})

    ############################
    # Publicly Exposed Methods #
    ############################

    def __enter__(self) -> Self:
        server = ThreadingHTTPServer((self.HOST, 0), CertsRequestHandler)
        server.stand_in = self  # type: ignore[attr-defined]
        self.server = server
        self.thread = threading.Thread(target=server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(
        self,
        error_type: Optional[Type[BaseException]],
        error: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
        if self.thread is not None:
            self.thread.join()

    @property
    def issuer_url(self) -> str:
        assert self.server is not None
        return f"http://{self.HOST}:{self.server.server_address[1]}{REALM_PATH}"

    @property
    def certs_requests(self) -> int:
        return self.certs_count

    def certs_body(self) -> bytes:
        self.certs_count += 1
        jwk: Dict[str, JsonValue] = json.loads(RSAAlgorithm.to_jwk(self.key.public_key()))
        jwk[self.KEY_ID_FIELD] = self.key_id
        keys: List[JsonValue] = [jwk]
        return json.dumps({self.KEYS_FIELD: keys}).encode(self.ENCODING)

    def mint(self, claims: Dict[str, JsonValue], expires_in_s: int = 300) -> str:
        return self.sign(self.key, self.key_id, claims, expires_in_s)

    def forge(self, claims: Dict[str, JsonValue], expires_in_s: int = 300) -> str:
        return self.sign(self.new_key(), uuid4().hex, claims, expires_in_s)

    def rotate(self) -> None:
        self.key = self.new_key()
        self.key_id = uuid4().hex
