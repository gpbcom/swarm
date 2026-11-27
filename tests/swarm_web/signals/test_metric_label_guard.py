from __future__ import annotations

# Standard library imports
from typing import ClassVar, List

# Third-party imports
from opentelemetry.proto.metrics.v1.metrics_pb2 import NumberDataPoint

# First-party imports
from swarm_web.models.config.signals_config import SignalsConfig
from swarm_web.models.enums import SignalAttribute
from swarm_web.signals.signals_configurator import SignalsConfigurator
from tests.fakes.otlp.otlp_stand_in_server import OtlpStandInServer


class TestMetricLabelGuard:
    COUNTER: ClassVar[str] = "frames_total"
    MISSION: ClassVar[str] = "mission-9"
    TOTAL: ClassVar[int] = 3

    def points(self, server: OtlpStandInServer) -> List[NumberDataPoint]:
        provider = SignalsConfigurator(SignalsConfig(endpoint=server.url)).meter_provider()
        counter = provider.get_meter("test").create_counter(self.COUNTER)
        counter.add(1, {SignalAttribute.DRONE_ID: "A", SignalAttribute.MISSION_ID: self.MISSION})
        counter.add(2, {SignalAttribute.DRONE_ID: "B", SignalAttribute.MISSION_ID: self.MISSION})
        assert provider.force_flush()
        groups = list(server.resource_metrics)
        provider.shutdown()
        return [
            point
            for group in groups
            for scope in group.scope_metrics
            for metric in scope.metrics
            if metric.name == self.COUNTER
            for point in metric.sum.data_points
        ]

    def test_a_metric_arrives_without_the_drone_id(self, otlp_stand_in: OtlpStandInServer) -> None:
        points = self.points(otlp_stand_in)
        assert points
        for point in points:
            assert SignalAttribute.DRONE_ID not in OtlpStandInServer.attributes(point.attributes)

    def test_points_that_become_identical_are_merged(self, otlp_stand_in: OtlpStandInServer) -> None:
        points = self.points(otlp_stand_in)
        assert len(points) == 1
        assert max(points[0].as_int, points[0].as_double) == self.TOTAL
        assert OtlpStandInServer.attributes(points[0].attributes) == {SignalAttribute.MISSION_ID: self.MISSION}
