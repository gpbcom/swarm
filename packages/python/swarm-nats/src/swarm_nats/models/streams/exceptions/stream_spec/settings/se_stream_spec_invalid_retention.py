from __future__ import annotations

from swarm_nats.models.streams.exceptions.stream_spec.se_invalid_stream_spec_exception import (
    SEInvalidStreamSpecException,
)


class SEStreamSpecInvalidRetention(SEInvalidStreamSpecException):
    """Exception raised when an invalid ``retention`` is provided."""
