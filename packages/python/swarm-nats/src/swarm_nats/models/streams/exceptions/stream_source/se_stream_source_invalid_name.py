from __future__ import annotations

from swarm_nats.models.streams.exceptions.stream_source.se_invalid_stream_source_exception import (
    SEInvalidStreamSourceException,
)


class SEStreamSourceInvalidName(SEInvalidStreamSourceException):
    """Exception raised when an invalid ``name`` is provided."""
