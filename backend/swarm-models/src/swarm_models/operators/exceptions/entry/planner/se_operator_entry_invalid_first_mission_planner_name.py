from __future__ import annotations

# First-party imports
from swarm_models.operators.exceptions.entry.se_invalid_operator_entry_exception import SEInvalidOperatorEntryException


class SEOperatorEntryInvalidFirstMissionPlannerName(SEInvalidOperatorEntryException):
    """Exception raised when an invalid ``first_mission_planner_name`` is provided."""
