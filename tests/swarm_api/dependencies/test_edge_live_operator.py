from __future__ import annotations

# Standard library imports
from typing import ClassVar
from uuid import UUID

# Third-party imports
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient

# First-party imports
from swarm_api.dependencies.edge_live_operator import EdgeLiveOperator


class TestEdgeLiveOperator:
    PATH: ClassVar[str] = "/edge"

    async def serve(self, websocket: WebSocket) -> None:
        operator_id = await EdgeLiveOperator()(websocket)
        await websocket.accept()
        await websocket.send_text(str(operator_id))
        await websocket.close()

    def test_the_edge_value_names_no_operator(self) -> None:
        assert EdgeLiveOperator.EDGE == UUID(int=0)

    def test_every_connection_of_the_edge_is_accepted_without_a_token(self) -> None:
        app = FastAPI()
        app.add_api_websocket_route(self.PATH, self.serve)

        with TestClient(app) as client, client.websocket_connect(self.PATH) as socket:
            assert socket.receive_text() == str(EdgeLiveOperator.EDGE)
