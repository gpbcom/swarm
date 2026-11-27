from __future__ import annotations

# First-party imports
from swarm_models.operators.exceptions.entry.se_invalid_operator_entry_exception import SEInvalidOperatorEntryException


class SEOperatorEntryInvalidLlmProvider(SEInvalidOperatorEntryException):
    """Exception raised when an invalid ``llm_provider`` is provided."""
