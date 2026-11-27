from __future__ import annotations

# Standard library imports
import logging
import warnings
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, Optional

# Third-party imports
from opentelemetry import _logs, metrics, propagate, trace
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

# First-party imports
from swarm_web.models.config.signals_config import SignalsConfig
from swarm_web.models.enums import SignalAttribute
from swarm_web.models.signals.signal_redaction_catalog import SignalRedactionCatalog
from swarm_web.signals.metric_label_guard import MetricLabelGuard
from swarm_web.signals.mission_span_processor import MissionSpanProcessor
from swarm_web.signals.redacting_span_exporter import RedactingSpanExporter


class SignalsConfigurator:
    """Sets up the OpenTelemetry SDK of a process: traces, metrics and logs, sent to the collector over OTLP/HTTP.

    Attributes:
        TRACES_SUFFIX (ClassVar[str]): The path of the traces on the collector.
        METRICS_SUFFIX (ClassVar[str]): The path of the metrics on the collector.
        LOGS_SUFFIX (ClassVar[str]): The path of the logs on the collector.
        MILLISECONDS_PER_SECOND (ClassVar[int]): The milliseconds in a second.
        SLASH (ClassVar[str]): The separator that ends an endpoint.
        config (SignalsConfig): The settings of the signals.
        logger (Logger): Logger instance.

    Notes:
        - ``tracer_provider`` and ``meter_provider`` build providers and install nothing: only ``configure`` sets the
          global providers, the log handler and the propagator.
        - Every span goes through the ``MissionSpanProcessor`` and the ``RedactingSpanExporter``, and every metric
          through the ``MetricLabelGuard``, so that no secret, no personal data and no ``drone_id`` label leaves.
        - The SDK flushes its exporters when the process exits.
    """

    TRACES_SUFFIX: ClassVar[str] = "/v1/traces"
    METRICS_SUFFIX: ClassVar[str] = "/v1/metrics"
    LOGS_SUFFIX: ClassVar[str] = "/v1/logs"
    MILLISECONDS_PER_SECOND: ClassVar[int] = 1000
    SLASH: ClassVar[str] = "/"

    def __init__(self, config: SignalsConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the configurator.

        Args:
            config (SignalsConfig): The settings of the signals.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _url(self, suffix: str) -> str:
        """Build the URL of a signal on the collector.

        Args:
            suffix (str): The path of the signal.

        Returns:
            str: The endpoint without its trailing slash, then the path.
        """
        return self.config.endpoint.rstrip(self.SLASH) + suffix

    def _logger_provider(self) -> LoggerProvider:
        """Build the logger provider, which exports the logs to the collector.

        Returns:
            LoggerProvider: The provider, not installed.
        """
        provider = LoggerProvider(resource=self.resource())
        provider.add_log_record_processor(
            BatchLogRecordProcessor(OTLPLogExporter(endpoint=self._url(self.LOGS_SUFFIX)))
        )
        self.logger.debug("Built the logger provider.")
        return provider

    ############################
    # Publicly Exposed Methods #
    ############################

    def resource(self) -> Resource:
        """Build the resource of the process.

        Returns:
            Resource: The resource, with the service name and the cell.
        """
        resource = Resource.create(
            {SERVICE_NAME: self.config.service_name, SignalAttribute.CELL.value: self.config.cell}
        )
        self.logger.debug("Built the resource of %s.", self.config.service_name)
        return resource

    def tracer_provider(self) -> TracerProvider:
        """Build the tracer provider.

        Returns:
            TracerProvider: The provider, not installed. Its spans carry the Mission and are redacted before export.
        """
        path = (
            Path(self.config.redactions_path) if self.config.redactions_path else SignalRedactionCatalog.REFERENCE_PATH
        )
        catalog = SignalRedactionCatalog.load(path)
        exporter = RedactingSpanExporter(OTLPSpanExporter(endpoint=self._url(self.TRACES_SUFFIX)), catalog)
        provider = TracerProvider(resource=self.resource())
        provider.add_span_processor(MissionSpanProcessor())
        provider.add_span_processor(BatchSpanProcessor(exporter))
        self.logger.debug("Built the tracer provider.")
        return provider

    def meter_provider(self) -> MeterProvider:
        """Build the meter provider.

        Returns:
            MeterProvider: The provider, not installed. Its metrics never carry a ``drone_id`` label.
        """
        exporter = MetricLabelGuard(OTLPMetricExporter(endpoint=self._url(self.METRICS_SUFFIX)))
        reader = PeriodicExportingMetricReader(
            exporter, export_interval_millis=int(self.config.metrics_interval_s * self.MILLISECONDS_PER_SECOND)
        )
        self.logger.debug("Built the meter provider.")
        return MeterProvider(resource=self.resource(), metric_readers=[reader])

    def configure(self) -> bool:
        """Install the providers, the log handler and the propagator of the process.

        Returns:
            bool: True when the signals are exported, False when they are disabled.
        """
        if not self.config.enabled:
            self.logger.debug("The signals are disabled.")
            return False
        trace.set_tracer_provider(self.tracer_provider())
        metrics.set_meter_provider(self.meter_provider())
        logger_provider = self._logger_provider()
        _logs.set_logger_provider(logger_provider)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
        logging.getLogger().addHandler(handler)
        propagate.set_global_textmap(CompositePropagator([TraceContextTextMapPropagator(), W3CBaggagePropagator()]))
        self.logger.info("Exporting the signals of %s to %s.", self.config.service_name, self.config.endpoint)
        return True
