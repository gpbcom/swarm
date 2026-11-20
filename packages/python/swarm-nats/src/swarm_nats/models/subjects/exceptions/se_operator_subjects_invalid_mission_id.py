from __future__ import annotations

from swarm_nats.models.subjects.exceptions.se_invalid_operator_subjects_exception import (
    SEInvalidOperatorSubjectsException,
)


class SEOperatorSubjectsInvalidMissionId(SEInvalidOperatorSubjectsException):
    """Exception raised when an invalid ``mission_id`` is provided."""
