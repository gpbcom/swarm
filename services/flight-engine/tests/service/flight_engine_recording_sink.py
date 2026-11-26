from __future__ import annotations

# Standard library imports
import asyncio
from typing import List, Tuple
from uuid import UUID

# First-party imports
from flight_engine.clients.leaf.frame_sink import FrameSink
from flight_engine.models.clients.exceptions import SESquadFramePublishError


class RecordingFrameSink(FrameSink):
    """A frame sink that records what it is given, and can be slow or failing.

    Attributes:
        published (List[Tuple[UUID, UUID, bytes]]): The ``(operator_id, mission_id, data)`` of each success.
        attempts (int): How many times ``publish`` was called.
        failing (bool): Whether ``publish`` raises ``SESquadFramePublishError``.
        delay_s (float): How long ``publish`` waits before it answers, in seconds.
    """

    def __init__(self, failing: bool = False, delay_s: float = 0.0) -> None:
        self.published: List[Tuple[UUID, UUID, bytes]] = []
        self.attempts = 0
        self.failing = failing
        self.delay_s = delay_s

    async def publish(self, operator_id: UUID, mission_id: UUID, data: bytes) -> None:
        self.attempts += 1
        if self.delay_s > 0:
            await asyncio.sleep(self.delay_s)
        if self.failing:
            raise SESquadFramePublishError("The recording sink was told to fail.")
        self.published.append((operator_id, mission_id, data))
