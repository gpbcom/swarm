from __future__ import annotations

# First-party imports
from swarm_models.subjects.exceptions.se_invalid_operator_subjects_exception import (
    SEInvalidOperatorSubjectsException,
)


class SEOperatorSubjectsInvalidOperatorId(SEInvalidOperatorSubjectsException):
    """Exception raised when an invalid ``operator_id`` is provided."""
