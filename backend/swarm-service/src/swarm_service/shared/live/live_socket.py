from __future__ import annotations

# Standard library imports
from typing import Protocol


class LiveSocket(Protocol):
    """What a live session needs of a WebSocket: binary messages in and out.

    Notes:
        - ``starlette.websockets.WebSocket`` satisfies it, and ``receive_bytes`` raises ``WebSocketDisconnect``
          once the client has left.
    """

    async def receive_bytes(self) -> bytes:
        """Wait for one message of the client.

        Returns:
            bytes: The message.
        """
        ...

    async def send_bytes(self, data: bytes) -> None:
        """Send one message to the client.

        Args:
            data (bytes): The message.
        """
        ...
