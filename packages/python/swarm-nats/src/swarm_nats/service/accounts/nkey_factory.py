from __future__ import annotations

# Standard library imports
import secrets
from logging import Logger, getLogger
from typing import ClassVar, Dict, Optional

# Third-party imports
import nkeys  # type: ignore[import-untyped]
from nkeys import KeyPair  # type: ignore[import-untyped]

# First-party imports
from swarm_nats.models.accounts.exceptions import SENkeyInvalidSeedError
from swarm_nats.models.enums import NatsClaimType


class NkeyFactory:
    """Create NKey pairs for the operator, accounts and users of NATS, and restore them from seeds.

    Attributes:
        ENCODING (str): The encoding of seeds and public keys, which are ASCII.
        SEED_LENGTH (int): The number of raw bytes of an ed25519 seed.
        ROLE_PREFIXES (Dict[NatsClaimType, int]): The NKey role prefix byte of each kind of key.
        logger (Logger): Logger instance.

    Notes:
        - An NKey seed is the base32 text, without padding, of the seed prefix byte combined with the role prefix, the
          32 raw bytes of the ed25519 seed and a little-endian CRC16. It starts with ``SO``, ``SA`` or ``SU``.
        - The encoding is done by ``nkeys.encode_seed``, so that this class keeps no copy of the format.
        - **Seeds are secrets: they are never logged.**
    """

    ENCODING: ClassVar[str] = "utf-8"
    SEED_LENGTH: ClassVar[int] = 32
    ROLE_PREFIXES: ClassVar[Dict[NatsClaimType, int]] = {
        NatsClaimType.OPERATOR: nkeys.PREFIX_BYTE_OPERATOR,
        NatsClaimType.ACCOUNT: nkeys.PREFIX_BYTE_ACCOUNT,
        NatsClaimType.USER: nkeys.PREFIX_BYTE_USER,
    }

    def __init__(self, logger: Optional[Logger] = None) -> None:
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def create(self, kind: NatsClaimType) -> KeyPair:
        """Create a new key pair of one kind.

        Args:
            kind (NatsClaimType): The role of the key: operator, account or user.

        Returns:
            KeyPair: The new key pair.

        Notes:
            - The raw seed comes from the ``secrets`` module, which draws from the operating system.
        """
        prefix = self.ROLE_PREFIXES[kind]
        raw = secrets.token_bytes(self.SEED_LENGTH)
        encoded = nkeys.encode_seed(raw, prefix)
        pair = nkeys.from_seed(encoded)
        self.logger.debug("Created a %s key pair.", kind)
        return pair

    def from_seed(self, seed: str) -> KeyPair:
        """Restore a key pair from its seed.

        Args:
            seed (str): The seed text, starting with ``S``.

        Returns:
            KeyPair: The key pair of that seed.

        Raises:
            SENkeyInvalidSeedError: When the seed is not a valid NKey seed.
        """
        try:
            pair = nkeys.from_seed(seed.encode(self.ENCODING))
        except (nkeys.NkeysError, ValueError) as error:
            self.logger.error("A seed was refused: %s.", type(error).__name__)
            raise SENkeyInvalidSeedError("Invalid seed. Must be a valid NKey seed.") from error
        self.logger.debug("Restored a key pair from a seed.")
        return pair

    def public_key(self, pair: KeyPair) -> str:
        """Give the public key of a pair.

        Args:
            pair (KeyPair): The key pair.

        Returns:
            str: The public key, 56 characters starting with ``O``, ``A`` or ``U``.
        """
        return bytes(pair.public_key).decode(self.ENCODING)

    def seed(self, pair: KeyPair) -> str:
        """Give the seed of a pair.

        Args:
            pair (KeyPair): The key pair.

        Returns:
            str: The seed, 58 characters starting with ``SO``, ``SA`` or ``SU``.

        Notes:
            - **The seed is a secret: the caller never logs it.**
        """
        return bytes(pair.seed).decode(self.ENCODING)
