from __future__ import annotations

# Standard library imports
from typing import Callable

# Third-party imports
import pytest
from fastapi.testclient import TestClient
from gateway_stand_in_live_source import GatewayStandInLiveSource


@pytest.fixture
def stand_in_source() -> GatewayStandInLiveSource:
    return GatewayStandInLiveSource([GatewayStandInLiveSource.FRAME])


@pytest.fixture
def make_client(stand_in_source: GatewayStandInLiveSource) -> Callable[[bool], TestClient]:
    return stand_in_source.build_client
