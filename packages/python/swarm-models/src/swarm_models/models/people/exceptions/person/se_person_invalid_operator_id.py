from __future__ import annotations

# First-party imports
from swarm_models.models.people.exceptions.person.se_invalid_person_exception import SEInvalidPersonException


class SEPersonInvalidOperatorId(SEInvalidPersonException):
    """Exception raised when an invalid ``operator_id`` is provided."""
