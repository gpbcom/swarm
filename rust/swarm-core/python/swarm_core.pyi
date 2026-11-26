from __future__ import annotations  # noqa: PYI044

from typing import Sequence

def safety_tick(values: Sequence[int]) -> int:
    """Return the wrapping sum of the values, computed by the safety tick of the Rust core."""

def planner_plan(values: Sequence[int]) -> int:
    """Return the wrapping sum of the values, computed by the planner of the Rust core."""

def mavlink_encode(values: Sequence[int]) -> int:
    """Return the wrapping sum of the values, computed by the MAVLink encoder of the Rust core."""

class DroneSample:
    """What the flight engine knows of one Drone, from its latest frames."""

    system_id: int
    has_position: bool
    lat_e7: int
    lon_e7: int
    relative_alt_mm: int
    vx_cm_s: int
    vy_cm_s: int
    hdg_cdeg: int
    battery_remaining: int
    base_mode: int
    system_status: int
    received: int
    lost: int
    updated_at_us: int

class LatestFrames:
    """The latest frame of each Drone, kept by the Rust core."""

    def __init__(self) -> None: ...
    def ingest(self, datagram: bytes, now_us: int) -> int:
        """Take the well-formed frames of the datagram and return how many there were."""

    def snapshot(self) -> list[DroneSample]:
        """Return the sample of every Drone heard from, ordered by system id."""
