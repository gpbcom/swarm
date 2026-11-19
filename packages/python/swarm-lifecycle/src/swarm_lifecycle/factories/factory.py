from __future__ import annotations

# Standard library imports
from abc import ABC, abstractmethod
from logging import Logger, getLogger
from typing import Optional


class Factory[T](ABC):
    """Base class of every factory, which builds one kind of product.

    Attributes:
        logger (Logger): Logger instance.

    Notes:
        - Subclasses implement ``_build`` only, and callers use ``create``, so that each product is logged the same way.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the factory.

        Args:
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    @abstractmethod
    def _build(self) -> T:
        """Build one product.

        Returns:
            T: A new product.
        """

    ############################
    # Publicly Exposed Methods #
    ############################

    def create(self) -> T:
        """Create one product.

        Returns:
            T: A new product.
        """
        product = self._build()
        self.logger.debug("Created %s.", type(product).__name__)
        return product
