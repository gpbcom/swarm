from __future__ import annotations

# First-party imports
from swarm_models.rest.problems.exceptions.se_invalid_problem_exception import (
    SEInvalidProblemException,
)


class SEProblemInvalidInstance(SEInvalidProblemException):
    """Exception raised when an invalid ``instance`` is provided."""
