from __future__ import annotations

# First-party imports
from swarm_rest.models.problems.exceptions.se_invalid_problem_exception import (
    SEInvalidProblemException,
)


class SEProblemInvalidTitle(SEInvalidProblemException):
    """Exception raised when an invalid ``title`` is provided."""
