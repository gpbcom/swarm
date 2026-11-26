from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional

# First-party imports
from swarm_web.models.rest.exceptions import SEPreconditionFailedError, SEPreconditionRequiredError


class EntityTag:
    """The entity tag of a resource: how a row version is shown, and how ``If-Match`` is checked against it.

    Attributes:
        ETAG_HEADER (ClassVar[str]): The name of the response header that carries the tag.
        IF_MATCH_HEADER (ClassVar[str]): The name of the request header that carries the expected tag.
        QUOTE (ClassVar[str]): The character that surrounds a tag.
        ANY (ClassVar[str]): The ``If-Match`` value that matches any current version.
        SEPARATOR (ClassVar[str]): Separates the tags of an ``If-Match`` list.
        logger (Logger): Logger instance.

    Notes:
        - The comparison is strong: a weak tag, which starts with ``W/``, never matches.
    """

    ETAG_HEADER: ClassVar[str] = "ETag"
    IF_MATCH_HEADER: ClassVar[str] = "If-Match"
    QUOTE: ClassVar[str] = '"'
    ANY: ClassVar[str] = "*"
    SEPARATOR: ClassVar[str] = ","

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the entity tag helper.

        Args:
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def format(self, version: int) -> str:
        """Format a row version as an entity tag.

        Args:
            version (int): The row version.

        Returns:
            str: The version between double quotes.
        """
        return f"{self.QUOTE}{version}{self.QUOTE}"

    def check_if_match(self, header: Optional[str], version: int) -> None:
        """Check an ``If-Match`` header against the current row version.

        Args:
            header (Optional[str]): The value of the ``If-Match`` header.
            version (int): The current row version.

        Raises:
            SEPreconditionRequiredError: If the header is missing or empty.
            SEPreconditionFailedError: If no tag of the header equals the current one.
        """
        if header is None or not header.strip():
            self.logger.error("The If-Match header is missing.")
            raise SEPreconditionRequiredError("The If-Match header is required.")
        if header.strip() == self.ANY:
            self.logger.debug("The If-Match header matches any version.")
            return
        current = self.format(version)
        for tag in header.split(self.SEPARATOR):
            if tag.strip() == current:
                self.logger.debug("The If-Match header holds the current tag.")
                return
        self.logger.error("The If-Match header holds no current tag.")
        raise SEPreconditionFailedError("The If-Match header does not match the current entity tag.")
