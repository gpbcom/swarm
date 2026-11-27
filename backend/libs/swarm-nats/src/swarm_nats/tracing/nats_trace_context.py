from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Dict, Optional

# Third-party imports
from opentelemetry.context import Context
from opentelemetry.propagate import extract, inject


class NatsTraceContext:
    """Carries the OpenTelemetry trace context in the headers of a NATS message.

    Attributes:
        logger (Logger): Logger instance.

    Notes:
        - The propagator is the global one, so whatever the logging and tracing configurator installs is used.
        - **``extract`` never raises**: a missing or malformed header gives an empty context.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def inject(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Return the headers plus the trace context of the current context.

        Args:
            headers (Optional[Dict[str, str]]): The headers to send, left unchanged.

        Returns:
            Dict[str, str]: A new dict with the given headers and the propagated ones.
        """
        carrier: Dict[str, str] = {}
        if headers:
            self.logger.debug("Copying %d headers before injecting the trace context.", len(headers))
            carrier.update(headers)
        else:
            self.logger.debug("No headers given, injecting the trace context alone.")
        inject(carrier)
        return carrier

    def extract(self, headers: Optional[Dict[str, str]]) -> Context:
        """Return the trace context carried by the headers of a received message.

        Args:
            headers (Optional[Dict[str, str]]): The headers received, if any.

        Returns:
            Context: The extracted context, or an empty one when there is none or it is malformed.
        """
        if not headers:
            self.logger.debug("No headers received, using an empty trace context.")
            return Context()
        try:
            return extract(headers)
        except (ValueError, TypeError, KeyError) as error:
            self.logger.debug("Malformed trace headers (%s), using an empty trace context.", type(error).__name__)
            return Context()
