from __future__ import annotations

from swarm_models.models.people.exceptions.person.se_invalid_person_exception import SEInvalidPersonException


class SEPersonInvalidEmail(SEInvalidPersonException):
    """Exception raised when an invalid ``email`` is provided."""
