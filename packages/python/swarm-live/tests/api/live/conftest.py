from __future__ import annotations

# Third-party imports
import pytest
from live_stand_in_socket import LiveStandInSocket

# First-party imports
from swarm_models.live.session.live_session_config import LiveSessionConfig  # isort: skip
from swarm_live.service.hub_live_source import HubLiveSource  # isort: skip
from swarm_live.service.live_codec import LiveCodec  # isort: skip
from swarm_live.service.live_hub import LiveHub  # isort: skip


@pytest.fixture
def stand_in_socket() -> LiveStandInSocket:
    return LiveStandInSocket()


@pytest.fixture
def hub() -> LiveHub:
    return LiveHub()


@pytest.fixture
def source(hub: LiveHub) -> HubLiveSource:
    return HubLiveSource(hub)


@pytest.fixture
def codec() -> LiveCodec:
    return LiveCodec()


@pytest.fixture
def config() -> LiveSessionConfig:
    return LiveSessionConfig(status_interval_s=0.05)
