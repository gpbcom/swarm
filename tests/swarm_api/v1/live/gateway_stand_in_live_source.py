from __future__ import annotations

# Standard library imports
from typing import ClassVar, List, Tuple
from uuid import UUID

# Third-party imports
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient

# First-party imports
from swarm_api.v1.live.live_router import LiveRouter
from swarm_models.live.live_subscription import LiveSubscription
from swarm_models.live.session.live_session_config import LiveSessionConfig
from swarm_service.shared.live.hub.live_mailbox import LiveMailbox
from swarm_service.shared.live.sources.live_source import LiveSource


class GatewayStandInLiveSource(LiveSource):
    """A live source that records joins and leaves, and hands out real mailboxes.

    Attributes:
        OPERATOR_ID (UUID): The Operator the tests connect as.
        OTHER_OPERATOR_ID (UUID): Another Operator, never to be used.
        MISSION_ID (UUID): The Mission the tests subscribe to.
        FRAME (bytes): The frame every mailbox starts with.
        frames (List[bytes]): The frames put in each mailbox as soon as it is handed out.
        operators (List[UUID]): The Operators that ``source_for`` was asked for.
        joins (List[Tuple[UUID, str]]): The Operator and topic of every join.
        leaves (List[str]): The topic of every leave.
        mailboxes (List[LiveMailbox]): The mailboxes handed out.
    """

    OPERATOR_ID: ClassVar[UUID] = UUID("01890a5d-ac96-774b-bcce-b302099a8057")
    OTHER_OPERATOR_ID: ClassVar[UUID] = UUID("01890a5d-ac96-774b-bcce-b302099a8058")
    MISSION_ID: ClassVar[UUID] = UUID("01890a5d-ac96-774b-bcce-b302099a8059")
    FRAME: ClassVar[bytes] = b"squad-frame"

    def __init__(self, frames: List[bytes]) -> None:
        self.frames = frames
        self.operators: List[UUID] = []
        self.joins: List[Tuple[UUID, str]] = []
        self.leaves: List[str] = []
        self.mailboxes: List[LiveMailbox] = []

    def source_for(self, operator_id: UUID) -> GatewayStandInLiveSource:
        """Remember the Operator and give back this source."""
        self.operators.append(operator_id)
        return self

    async def join(self, subscription: LiveSubscription) -> LiveMailbox:
        """Record the join and hand out a mailbox holding the frames."""
        mailbox = LiveMailbox()
        for frame in self.frames:
            mailbox.put(frame)
        self.mailboxes.append(mailbox)
        self.joins.append((self.operators[-1], subscription.topic))
        return mailbox

    async def leave(self, subscription: LiveSubscription, mailbox: LiveMailbox) -> None:
        """Record the leave."""
        self.leaves.append(subscription.topic)

    async def operator(self, websocket: WebSocket) -> UUID:
        """Give the Operator the tests connect as, for every connection."""
        return self.OPERATOR_ID

    def build_client(self, with_operator: bool) -> TestClient:
        """Build a client of an app that serves the live router over this source.

        Without ``with_operator``, the router keeps the gateway's ``LiveOperator``, which refuses every connection of
        an app that has no access check installed.
        """
        if with_operator:
            router = LiveRouter(self.source_for, LiveSessionConfig(status_interval_s=0.05), self.operator)
        else:
            router = LiveRouter(self.source_for, LiveSessionConfig(status_interval_s=0.05))
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
