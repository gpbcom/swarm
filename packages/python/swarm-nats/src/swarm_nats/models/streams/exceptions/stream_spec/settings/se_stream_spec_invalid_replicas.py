from __future__ import annotations

from swarm_nats.models.streams.exceptions.stream_spec.se_invalid_stream_spec_exception import (
    SEInvalidStreamSpecException,
)


class SEStreamSpecInvalidReplicas(SEInvalidStreamSpecException):
    """Exception raised when an invalid ``replicas`` is provided."""
