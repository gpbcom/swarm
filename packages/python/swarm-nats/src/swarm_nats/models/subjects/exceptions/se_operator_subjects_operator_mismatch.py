from __future__ import annotations

from swarm_nats.models.subjects.exceptions.se_invalid_operator_subjects_exception import (
    SEInvalidOperatorSubjectsException,
)


class SEOperatorSubjectsOperatorMismatch(SEInvalidOperatorSubjectsException):
    """Exception raised when an event belongs to another Operator."""
