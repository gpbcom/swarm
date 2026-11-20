from __future__ import annotations

# First-party imports
from swarm_rest.models.problems.exceptions.se_invalid_problem_exception import (
    SEInvalidProblemException,
)


class SEProblemInvalidType(SEInvalidProblemException):
    """Exception raised when an invalid ``type`` is provided."""
