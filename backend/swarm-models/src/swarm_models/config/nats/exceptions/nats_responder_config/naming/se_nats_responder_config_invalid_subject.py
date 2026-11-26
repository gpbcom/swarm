from __future__ import annotations

# First-party imports
from swarm_nats.models.config.exceptions.nats_responder_config.se_invalid_nats_responder_config_exception import (
    SEInvalidNatsResponderConfigException,
)


class SENatsResponderConfigInvalidSubject(SEInvalidNatsResponderConfigException):
    """Exception raised when an invalid ``subject`` is provided."""
