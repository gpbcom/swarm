from __future__ import annotations


class SEInvalidSimulationRequestException(ValueError):
    """Exception raised when an invalid SimulationRequest is provided.

    Notes:
        It is a ``ValueError``, so that Pydantic reports a body that does not validate as a validation error, which
        the api layer answers with ``422``.
    """
