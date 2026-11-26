from __future__ import annotations

# Standard library imports
import asyncio
from typing import List, Optional

# Third-party imports
from starlette.websockets import WebSocketDisconnect


class LiveStandInSocket:
    """A stand-in client socket: the test feeds what the client sends, and reads what the server sent.

    Attributes:
        send_delay_s (float): How long each ``send_bytes`` takes, to play a slow client.
        sent (List[bytes]): Every message sent to the client, in order.
        incoming (asyncio.Queue[Optional[bytes]]): What the client sent, ``None`` meaning it disconnected.
    """

    def __init__(self, send_delay_s: float = 0.0) -> None:
        self.send_delay_s = send_delay_s
        self.sent: List[bytes] = []
        self.incoming: asyncio.Queue[Optional[bytes]] = asyncio.Queue()

    def feed(self, data: bytes) -> None:
        """Make the client send one message."""
        self.incoming.put_nowait(data)

    def disconnect(self) -> None:
        """Make the client disconnect."""
        self.incoming.put_nowait(None)

    async def receive_bytes(self) -> bytes:
        """Wait for what the client sends, and raise ``WebSocketDisconnect`` once it left."""
        data = await self.incoming.get()
        if data is None:
            raise WebSocketDisconnect()
        return data

    async def send_bytes(self, data: bytes) -> None:
        """Take ``send_delay_s`` to send one message to the client, then record it."""
        await asyncio.sleep(self.send_delay_s)
        self.sent.append(data)

    async def wait_for_sent(self, count: int, timeout_s: float = 2.0) -> None:
        """Wait until at least ``count`` messages were sent, or fail after ``timeout_s``."""
        async with asyncio.timeout(timeout_s):
            while len(self.sent) < count:
                await asyncio.sleep(0.005)
