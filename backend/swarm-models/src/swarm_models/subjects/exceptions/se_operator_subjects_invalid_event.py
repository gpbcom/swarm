from __future__ import annotations

# First-party imports
from swarm_nats.models.subjects.exceptions.se_invalid_operator_subjects_exception import (
    SEInvalidOperatorSubjectsException,
)


class SEOperatorSubjectsInvalidEvent(SEInvalidOperatorSubjectsException):
    """Exception raised when an invalid ``event`` is provided."""
