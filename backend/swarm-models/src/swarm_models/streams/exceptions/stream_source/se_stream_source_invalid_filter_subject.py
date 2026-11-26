from __future__ import annotations

# First-party imports
from swarm_nats.models.streams.exceptions.stream_source.se_invalid_stream_source_exception import (
    SEInvalidStreamSourceException,
)


class SEStreamSourceInvalidFilterSubject(SEInvalidStreamSourceException):
    """Exception raised when an invalid ``filter_subject`` is provided."""
