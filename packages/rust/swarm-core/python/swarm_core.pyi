from __future__ import annotations  # noqa: PYI044

from typing import Sequence

def safety_tick(values: Sequence[int]) -> int:
    """Return the wrapping sum of the values, computed by the safety tick of the Rust core."""

def planner_plan(values: Sequence[int]) -> int:
    """Return the wrapping sum of the values, computed by the planner of the Rust core."""

def mavlink_encode(values: Sequence[int]) -> int:
    """Return the wrapping sum of the values, computed by the MAVLink encoder of the Rust core."""
