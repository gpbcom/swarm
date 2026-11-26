from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Dict, List, Optional, Tuple

# First-party imports
from swarm_service.shared.live.hub.live_mailbox import LiveMailbox


class LiveHub:
    """Fan frames out to the mailboxes of the clients that watch each key.

    Attributes:
        mailboxes (Dict[str, List[LiveMailbox]]): The mailboxes of each key, in the order they subscribed.
        logger (Logger): Logger instance.

    Notes:
        - A publish never waits for a client:
          it puts the frame in each mailbox,
          where it replaces an unread one.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise an empty hub.

        Args:
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.mailboxes: Dict[str, List[LiveMailbox]] = {}

    ############################
    # Publicly Exposed Methods #
    ############################

    def subscribe(self, key: str) -> Tuple[LiveMailbox, bool]:
        """Give a client a new mailbox on a key.

        Args:
            key (str): The key to watch.

        Returns:
            Tuple[LiveMailbox, bool]: The mailbox, and True when this is the first watcher of the key.
        """
        mailbox = LiveMailbox()
        watchers = self.mailboxes.setdefault(key, [])
        first = not watchers
        watchers.append(mailbox)
        if first:
            self.logger.debug("First watcher of %s.", key)
        else:
            self.logger.debug("Watcher %d of %s.", len(watchers), key)
        return mailbox, first

    def unsubscribe(self, key: str, mailbox: LiveMailbox) -> bool:
        """Remove a client's mailbox from a key.

        Args:
            key (str): The key that was watched.
            mailbox (LiveMailbox): The mailbox given by ``subscribe``.

        Returns:
            bool: True when the last watcher of the key left.
        """
        watchers = self.mailboxes.get(key)
        if watchers is None or mailbox not in watchers:
            self.logger.debug("Mailbox was not watching %s.", key)
            return False
        watchers.remove(mailbox)
        if watchers:
            self.logger.debug("%d watchers left on %s.", len(watchers), key)
            return False
        del self.mailboxes[key]
        self.logger.debug("Last watcher left %s.", key)
        return True

    def publish(self, key: str, data: bytes) -> int:
        """Put a frame in the mailbox of every watcher of a key.

        Args:
            key (str): The key.
            data (bytes): The encoded frame.

        Returns:
            int: The number of mailboxes reached.
        """
        watchers = self.mailboxes.get(key)
        if not watchers:
            self.logger.debug("No watcher on %s.", key)
            return 0
        for mailbox in watchers:
            mailbox.put(data)
        self.logger.debug("Published to %d watchers of %s.", len(watchers), key)
        return len(watchers)

    def watchers(self, key: str) -> int:
        """Count the watchers of a key.

        Args:
            key (str): The key.

        Returns:
            int: The number of mailboxes on the key.
        """
        return len(self.mailboxes.get(key, []))
