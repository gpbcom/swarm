from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List, Optional

# Third-party imports
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import Counter, Histogram, MeterProvider
from opentelemetry.sdk.metrics.export import AggregationTemporality, DataPointT, InMemoryMetricReader
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


class RecordedSignals:
    """The spans and metrics the code under test records, kept in memory.

    Attributes:
        TEMPORALITY (Dict[type, AggregationTemporality]): Delta for counters and histograms, so that ``clear`` empties them.
        instance (Optional[RecordedSignals]): The one instance of the process.
        span_exporter (InMemorySpanExporter): Holds the finished spans.
        metric_reader (InMemoryMetricReader): Reads the recorded metrics.

    Notes:
        - The global providers can be set once per process, so the instance is created once and reused.
        - **A global meter provider installed by someone else cannot take our reader**: no metric is then recorded.
    """

    TEMPORALITY: ClassVar[Dict[type, AggregationTemporality]] = {
        Counter: AggregationTemporality.DELTA,
        Histogram: AggregationTemporality.DELTA,
    }
    instance: ClassVar[Optional[RecordedSignals]] = None

    def __init__(self) -> None:
        self.span_exporter = InMemorySpanExporter()
        self.metric_reader = InMemoryMetricReader(preferred_temporality=self.TEMPORALITY)
        self.collected: Dict[str, List[DataPointT]] = {}
        tracer_provider = trace.get_tracer_provider()
        if not isinstance(tracer_provider, TracerProvider):
            tracer_provider = TracerProvider()
            trace.set_tracer_provider(tracer_provider)
        tracer_provider.add_span_processor(SimpleSpanProcessor(self.span_exporter))
        if not isinstance(metrics.get_meter_provider(), MeterProvider):
            metrics.set_meter_provider(MeterProvider(metric_readers=[self.metric_reader]))

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def get(cls) -> RecordedSignals:
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

    def spans(self) -> List[ReadableSpan]:
        return list(self.span_exporter.get_finished_spans())

    def metric_points(self, name: str) -> List[DataPointT]:
        data = self.metric_reader.get_metrics_data()
        if data is not None:
            for resource_metrics in data.resource_metrics:
                for scope_metrics in resource_metrics.scope_metrics:
                    for metric in scope_metrics.metrics:
                        self.collected.setdefault(metric.name, []).extend(metric.data.data_points)
        return list(self.collected.get(name, []))

    def clear(self) -> None:
        self.span_exporter.clear()
        self.metric_reader.get_metrics_data()
        self.collected.clear()
