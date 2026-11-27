from __future__ import annotations

# Standard library imports
from typing import ClassVar

# Third-party imports
from opentelemetry import baggage, context

# First-party imports
from swarm_web.models.config.signals_config import SignalsConfig
from swarm_web.models.enums import SignalAttribute
from swarm_web.signals.signals_configurator import SignalsConfigurator
from tests.fakes.otlp.otlp_stand_in_server import OtlpStandInServer


class TestMissionSpanProcessor:
    OPERATOR: ClassVar[str] = "operator-1"
    MISSION: ClassVar[str] = "mission-9"

    def received(self, server: OtlpStandInServer, with_baggage: bool) -> OtlpStandInServer:
        provider = SignalsConfigurator(SignalsConfig(endpoint=server.url)).tracer_provider()
        parent = context.get_current()
        if with_baggage:
            parent = baggage.set_baggage(SignalAttribute.OPERATOR_ID, self.OPERATOR, parent)
            parent = baggage.set_baggage(SignalAttribute.MISSION_ID, self.MISSION, parent)
        with provider.get_tracer("test").start_as_current_span("mission", context=parent):
            pass
        assert provider.force_flush()
        provider.shutdown()
        return server

    def test_a_span_under_baggage_carries_the_operator_and_the_mission(self, otlp_stand_in: OtlpStandInServer) -> None:
        span = self.received(otlp_stand_in, with_baggage=True).spans[0]
        attributes = OtlpStandInServer.attributes(span.attributes)
        assert attributes[SignalAttribute.OPERATOR_ID] == self.OPERATOR
        assert attributes[SignalAttribute.MISSION_ID] == self.MISSION

    def test_a_span_without_baggage_carries_neither(self, otlp_stand_in: OtlpStandInServer) -> None:
        span = self.received(otlp_stand_in, with_baggage=False).spans[0]
        attributes = OtlpStandInServer.attributes(span.attributes)
        assert SignalAttribute.OPERATOR_ID not in attributes
        assert SignalAttribute.MISSION_ID not in attributes
