from __future__ import annotations

# Standard library imports
from asyncio import DatagramProtocol
from logging import Logger, getLogger
from typing import Callable, Optional, Tuple, Union


class MavlinkDatagramProtocol(DatagramProtocol):
    """The asyncio protocol of the MAVLink UDP endpoint: it hands each datagram to a callback.

    Attributes:
        on_datagram (Callable[[bytes], None]): Called with the bytes of each datagram.
        logger (Logger): Logger instance.
    """

    def __init__(self, on_datagram: Callable[[bytes], None], logger: Optional[Logger] = None) -> None:
        """Keep the callback.

        Args:
            on_datagram (Callable[[bytes], None]): Called with the bytes of each datagram.
            logger (Optional[Logger]): Logger instance.
        """
        self.on_datagram = on_datagram
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def datagram_received(self, data: bytes, addr: Tuple[Union[str, int], ...]) -> None:
        """Hand one datagram to the callback.

        Args:
            data (bytes): The datagram.
            addr (Tuple[Union[str, int], ...]): The sender, unused.
        """
        self.on_datagram(data)

    def error_received(self, exc: Exception) -> None:
        """Log an error of the UDP endpoint.

        Args:
            exc (Exception): The error.
        """
        self.logger.warning("The MAVLink endpoint reported %s.", type(exc).__name__)
