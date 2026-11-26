from __future__ import annotations

# First-party imports
from swarm_models.people.exceptions.person.se_invalid_person_exception import SEInvalidPersonException


class SEPersonInvalidLanguage(SEInvalidPersonException):
    """Exception raised when an invalid ``language`` is provided."""
