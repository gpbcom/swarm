from __future__ import annotations

# Standard library imports
import json
from logging import Logger, getLogger
from typing import ClassVar, Optional

# Third-party imports
from nats.aio.client import Client
from nats.errors import Error as NatsError
from nats.errors import TimeoutError as NatsTimeoutError
from pydantic import JsonValue

# First-party imports
from swarm_nats.models.accounts.issued_account import IssuedAccount
from swarm_nats.models.bus.exceptions import SENatsAccountPushRefusedError


class AccountResolverClient:
    """Pushes the JWT of an account to the resolver of the NATS servers.

    Attributes:
        CLAIMS_UPDATE_SUBJECT (ClassVar[str]): The subject of the system account that updates an account.
        ENCODING (ClassVar[str]): The encoding of the request and of the reply.
        ERROR_KEY (ClassVar[str]): The key of the reply that holds an error.
        connection (Client): A client connected with the credentials of the system account.
        timeout_s (float): How long to wait for the reply, in seconds.
        logger (Logger): Logger instance.

    Notes:
        - **The connection must use the system account**, otherwise nothing answers the claims update subject.
        - It works against the full resolver the chart ``deploy/charts/nats`` configures, which stores the JWT and
          shares it with the other servers of the cell.
        - A revocation is a new JWT of the same account, pushed the same way.
        - **The JWT is never logged**, only the name and the public key of the account.
    """

    CLAIMS_UPDATE_SUBJECT: ClassVar[str] = "$SYS.REQ.CLAIMS.UPDATE"
    ENCODING: ClassVar[str] = "utf-8"
    ERROR_KEY: ClassVar[str] = "error"

    def __init__(self, connection: Client, timeout_s: float, logger: Optional[Logger] = None) -> None:
        """Keep the connection and the timeout.

        Args:
            connection (Client): A client connected with the credentials of the system account.
            timeout_s (float): How long to wait for the reply, in seconds.
            logger (Optional[Logger]): Logger instance.
        """
        self.connection = connection
        self.timeout_s = timeout_s
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def push(self, account: IssuedAccount) -> None:
        """Push the JWT of an account to the resolver.

        Args:
            account (IssuedAccount): The account, whose JWT is sent.

        Raises:
            SENatsAccountPushRefusedError: When the reply holds an error, nothing answers in time or the reply is
                not JSON.
        """
        self.logger.debug("Pushing the account %s.", account.name)
        try:
            message = await self.connection.request(
                self.CLAIMS_UPDATE_SUBJECT, account.jwt.encode(self.ENCODING), timeout=self.timeout_s
            )
        except NatsTimeoutError as error:
            self.logger.error("Nothing answered the push of the account %s within %s s.", account.name, self.timeout_s)
            raise SENatsAccountPushRefusedError(
                f"Invalid account: {account.name!r}. Nothing answered the push within {self.timeout_s} s."
            ) from error
        except NatsError as error:
            self.logger.error("The push of the account %s failed: %s.", account.name, type(error).__name__)
            raise SENatsAccountPushRefusedError(
                f"Invalid account: {account.name!r}. The push failed with {type(error).__name__}."
            ) from error
        try:
            reply: JsonValue = json.loads(message.data.decode(self.ENCODING))
        except (ValueError, UnicodeDecodeError) as error:
            self.logger.error("The reply to the push of the account %s is not JSON.", account.name)
            raise SENatsAccountPushRefusedError(
                f"Invalid reply: to the push of the account {account.name!r}. Must be JSON."
            ) from error
        if isinstance(reply, dict) and self.ERROR_KEY in reply:
            self.logger.error("The resolver refused the account %s.", account.name)
            raise SENatsAccountPushRefusedError(f"Invalid account: {account.name!r}. The resolver refused it.")
        self.logger.info("Pushed the account %s with the public key %s.", account.name, account.public_key)
