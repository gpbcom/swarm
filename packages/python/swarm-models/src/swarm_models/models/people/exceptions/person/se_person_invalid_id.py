from __future__ import annotations

from swarm_models.models.people.exceptions.person.se_invalid_person_exception import SEInvalidPersonException


class SEPersonInvalidId(SEInvalidPersonException):
    """Exception raised when an invalid ``id`` is provided."""
