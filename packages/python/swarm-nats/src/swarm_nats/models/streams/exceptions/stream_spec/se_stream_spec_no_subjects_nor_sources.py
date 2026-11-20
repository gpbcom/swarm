from __future__ import annotations

# First-party imports
from swarm_nats.models.streams.exceptions.stream_spec.se_invalid_stream_spec_exception import (
    SEInvalidStreamSpecException,
)


class SEStreamSpecNoSubjectsNorSources(SEInvalidStreamSpecException):
    """Exception raised when a StreamSpec has neither subjects nor sources."""
