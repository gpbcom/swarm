from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from typing import Optional


class LiveMailbox:
    """A one-slot mailbox that holds the latest frame of a topic for one client.

    Attributes:
        slot (Optional[bytes]): The unread frame, if any.
        event (asyncio.Event): Set while the slot holds a frame.
        skipped (int): How many frames were replaced before they were read.
        delivered (int): How many frames were taken.
        logger (Logger): Logger instance.

    Notes:
        - **The mailbox never queues**: a frame put while another is unread replaces it, so a slow client skips
          intermediate frames and memory stays bounded.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise an empty mailbox.

        Args:
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.slot: Optional[bytes] = None
        self.event = asyncio.Event()
        self.skipped = 0
        self.delivered = 0

    ############################
    # Publicly Exposed Methods #
    ############################

    def put(self, data: bytes) -> None:
        """Put a frame in the slot, replacing an unread one.

        Args:
            data (bytes): The encoded frame.
        """
        if self.slot is not None:
            self.skipped += 1
            self.logger.debug("Replaced an unread frame, %d skipped.", self.skipped)
        else:
            self.logger.debug("Filled an empty slot.")
        self.slot = data
        self.event.set()

    def pending(self) -> bool:
        """Tell whether a frame is waiting.

        Returns:
            bool: True when the slot is full.
        """
        return self.slot is not None

    async def take(self) -> bytes:
        """Wait for a frame, remove it from the slot and return it.

        Returns:
            bytes: The latest frame.
        """
        await self.event.wait()
        data = self.slot
        self.slot = None
        self.event.clear()
        if data is None:
            self.logger.debug("Woken with an empty slot.")
            return await self.take()
        self.delivered += 1
        self.logger.debug("Delivered frame %d.", self.delivered)
        return data
