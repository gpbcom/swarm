from __future__ import annotations

# Standard library imports
import json
import subprocess
import sys
from typing import ClassVar, Dict, List

# Third-party imports
from opentelemetry import trace

# First-party imports
from swarm_web.models.config.signals_config import SignalsConfig
from swarm_web.models.enums import SignalAttribute
from swarm_web.signals.signals_configurator import SignalsConfigurator
from tests.fakes.otlp.otlp_stand_in_server import OtlpStandInServer


class TestSignalsConfigurator:
    SERVICE_NAME: ClassVar[str] = "swarm-test"
    CELL: ClassVar[str] = "cell-7"
    SERVICE_NAME_KEY: ClassVar[str] = "service.name"
    SPAN_NAME: ClassVar[str] = "the-work"
    METRIC_NAME: ClassVar[str] = "the_work_total"
    LOG_MESSAGE: ClassVar[str] = "a-logged-message"
    ANSWER_KEY: ClassVar[str] = "answer"
    INSTALLED_KEY: ClassVar[str] = "installed"
    FIELDS_KEY: ClassVar[str] = "fields"
    PROPAGATION_FIELDS: ClassVar[List[str]] = ["traceparent", "baggage"]
    TIMEOUT_S: ClassVar[float] = 60.0
    CHILD_CODE: ClassVar[str] = """
import json
import logging
import sys
from opentelemetry import propagate, trace
from opentelemetry.sdk.trace import TracerProvider
from swarm_web.models.config.signals_config import SignalsConfig
from swarm_web.signals.signals_configurator import SignalsConfigurator

config = SignalsConfig(enabled=True, endpoint=sys.argv[1], service_name=sys.argv[2], cell=sys.argv[3])
answer = SignalsConfigurator(config).configure()
with trace.get_tracer("child").start_as_current_span(sys.argv[4]):
    logging.getLogger("child").warning(sys.argv[5])
provider = trace.get_tracer_provider()
installed = isinstance(provider, TracerProvider)
fields = sorted(propagate.get_global_textmap().fields)
provider.shutdown()
print(json.dumps({"answer": answer, "installed": installed, "fields": fields}))
"""

    def config(self, server: OtlpStandInServer, enabled: bool = True) -> SignalsConfig:
        return SignalsConfig(
            enabled=enabled,
            endpoint=server.url,
            service_name=self.SERVICE_NAME,
            cell=self.CELL,
            metrics_interval_s=1.0,
        )

    def test_the_resource_carries_the_service_name_and_the_cell(self, otlp_stand_in: OtlpStandInServer) -> None:
        resource = SignalsConfigurator(self.config(otlp_stand_in)).resource()
        assert resource.attributes[self.SERVICE_NAME_KEY] == self.SERVICE_NAME
        assert resource.attributes[SignalAttribute.CELL] == self.CELL

    def test_a_span_arrives_with_the_service_name_and_the_cell(self, otlp_stand_in: OtlpStandInServer) -> None:
        provider = SignalsConfigurator(self.config(otlp_stand_in)).tracer_provider()
        with provider.get_tracer("test").start_as_current_span(self.SPAN_NAME):
            pass
        assert provider.force_flush()
        groups = otlp_stand_in.resource_spans
        assert len(groups) == 1
        resource = OtlpStandInServer.attributes(groups[0].resource.attributes)
        assert resource[self.SERVICE_NAME_KEY] == self.SERVICE_NAME
        assert resource[SignalAttribute.CELL] == self.CELL
        assert [span.name for span in otlp_stand_in.spans] == [self.SPAN_NAME]
        provider.shutdown()

    def test_a_metric_arrives_with_the_service_name_and_the_cell(self, otlp_stand_in: OtlpStandInServer) -> None:
        provider = SignalsConfigurator(self.config(otlp_stand_in)).meter_provider()
        provider.get_meter("test").create_counter(self.METRIC_NAME).add(1)
        assert provider.force_flush()
        groups = otlp_stand_in.resource_metrics
        assert len(groups) == 1
        resource = OtlpStandInServer.attributes(groups[0].resource.attributes)
        assert resource[self.SERVICE_NAME_KEY] == self.SERVICE_NAME
        assert resource[SignalAttribute.CELL] == self.CELL
        provider.shutdown()

    def test_the_build_methods_install_nothing_globally(self, otlp_stand_in: OtlpStandInServer) -> None:
        before = trace.get_tracer_provider()
        configurator = SignalsConfigurator(self.config(otlp_stand_in))
        configurator.tracer_provider().shutdown()
        configurator.meter_provider().shutdown()
        assert trace.get_tracer_provider() is before

    def test_a_disabled_configuration_installs_nothing(self, otlp_stand_in: OtlpStandInServer) -> None:
        before = trace.get_tracer_provider()
        assert SignalsConfigurator(self.config(otlp_stand_in, enabled=False)).configure() is False
        assert trace.get_tracer_provider() is before

    def test_an_enabled_configuration_installs_the_providers_in_a_child_process(
        self, otlp_stand_in: OtlpStandInServer
    ) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                self.CHILD_CODE,
                otlp_stand_in.url,
                self.SERVICE_NAME,
                self.CELL,
                self.SPAN_NAME,
                self.LOG_MESSAGE,
            ],
            capture_output=True,
            text=True,
            timeout=self.TIMEOUT_S,
            check=True,
        )
        report: Dict[str, List[str] | bool] = json.loads(completed.stdout.strip().splitlines()[-1])
        assert report[self.ANSWER_KEY] is True
        assert report[self.INSTALLED_KEY] is True
        assert set(self.PROPAGATION_FIELDS) <= set(report[self.FIELDS_KEY])
        assert [span.name for span in otlp_stand_in.spans] == [self.SPAN_NAME]
        bodies = [
            record.body.string_value
            for group in otlp_stand_in.resource_logs
            for scope in group.scope_logs
            for record in scope.log_records
        ]
        assert self.LOG_MESSAGE in bodies
