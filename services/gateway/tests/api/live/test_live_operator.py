from __future__ import annotations

# Standard library imports
from typing import Callable

# Third-party imports
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


class TestLiveOperator:
    LIVE_PATH = "/v1/live"
    POLICY_VIOLATION = 1008

    def test_a_connection_without_an_operator_is_closed_as_a_policy_violation(
        self, make_client: Callable[[bool], TestClient]
    ) -> None:
        client = make_client(False)
        with pytest.raises(WebSocketDisconnect) as raised, client.websocket_connect(self.LIVE_PATH) as socket:
            socket.receive_bytes()
        assert raised.value.code == self.POLICY_VIOLATION
