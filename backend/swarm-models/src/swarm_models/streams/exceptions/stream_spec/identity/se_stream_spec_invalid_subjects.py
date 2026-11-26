from __future__ import annotations

# First-party imports
from swarm_nats.models.streams.exceptions.stream_spec.se_invalid_stream_spec_exception import (
    SEInvalidStreamSpecException,
)


class SEStreamSpecInvalidSubjects(SEInvalidStreamSpecException):
    """Exception raised when an invalid ``subjects`` is provided."""
