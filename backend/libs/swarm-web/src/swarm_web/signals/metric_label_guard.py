from __future__ import annotations

# Standard library imports
from dataclasses import replace
from logging import Logger, getLogger
from typing import ClassVar, Dict, List, Mapping, Optional, Sequence, Tuple

# Third-party imports
from opentelemetry.sdk.metrics.export import (
    Gauge,
    Histogram,
    HistogramDataPoint,
    Metric,
    MetricExporter,
    MetricExportResult,
    MetricsData,
    NumberDataPoint,
    ResourceMetrics,
    ScopeMetrics,
    Sum,
)
from opentelemetry.util.types import Attributes, AttributeValue

# First-party imports
from swarm_web.models.enums import SignalAttribute


class MetricLabelGuard(MetricExporter):
    """Exports metrics without the ``drone_id`` label, which would multiply the series by the size of a Squad.

    Attributes:
        FORBIDDEN (ClassVar[str]): The label that is never exported.
        inner (MetricExporter): The exporter that receives the metrics.
        logger (Logger): Logger instance.

    Notes:
        - The points that become identical once the label is gone are merged: sums add up, histograms add their
          counts, buckets and sums and keep the widest minimum and maximum, and a gauge keeps its last value.
        - **A metric of another kind is dropped**, because its points cannot be merged and would leak the label.
        - The temporality and the aggregation preferences are those of the inner exporter.
    """

    FORBIDDEN: ClassVar[str] = SignalAttribute.DRONE_ID.value

    def __init__(self, inner: MetricExporter, logger: Optional[Logger] = None) -> None:
        """Initialise the guard.

        Args:
            inner (MetricExporter): The exporter that receives the metrics.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__(
            preferred_temporality=inner._preferred_temporality, preferred_aggregation=inner._preferred_aggregation
        )
        self.inner = inner
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _strip(self, attributes: Attributes) -> Dict[str, AttributeValue]:
        """Remove the forbidden label from the attributes of a point.

        Args:
            attributes (Attributes): The attributes of a point.

        Returns:
            Dict[str, AttributeValue]: The attributes without the forbidden label.
        """
        return {key: value for key, value in (attributes or {}).items() if key != self.FORBIDDEN}

    def _identity(self, attributes: Mapping[str, AttributeValue]) -> Tuple[Tuple[str, str], ...]:
        """Build the key that tells whether two points share their attributes.

        Args:
            attributes (Mapping[str, AttributeValue]): The stripped attributes.

        Returns:
            Tuple[Tuple[str, str], ...]: The sorted pairs, with the values as text.
        """
        return tuple(sorted((key, repr(value)) for key, value in attributes.items()))

    def _merge_numbers(self, points: Sequence[NumberDataPoint], last_value: bool) -> List[NumberDataPoint]:
        """Merge number points that become identical.

        Args:
            points (Sequence[NumberDataPoint]): The points of a sum or of a gauge.
            last_value (bool): True to keep the latest value (a gauge), False to add the values (a sum).

        Returns:
            List[NumberDataPoint]: One point per set of attributes.
        """
        merged: Dict[Tuple[Tuple[str, str], ...], NumberDataPoint] = {}
        for point in points:
            attributes = self._strip(point.attributes)
            key = self._identity(attributes)
            known = merged.get(key)
            if known is None:
                merged[key] = replace(point, attributes=attributes)
                self.logger.debug("Kept a new point.")
            elif last_value:
                if point.time_unix_nano >= known.time_unix_nano:
                    merged[key] = replace(point, attributes=attributes)
                self.logger.debug("Kept the latest value of a gauge.")
            else:
                merged[key] = replace(
                    known,
                    value=known.value + point.value,
                    start_time_unix_nano=min(known.start_time_unix_nano, point.start_time_unix_nano),
                    time_unix_nano=max(known.time_unix_nano, point.time_unix_nano),
                )
                self.logger.debug("Added a point to another.")
        return list(merged.values())

    def _merge_histograms(self, points: Sequence[HistogramDataPoint]) -> List[HistogramDataPoint]:
        """Merge histogram points that become identical.

        Args:
            points (Sequence[HistogramDataPoint]): The points of a histogram.

        Returns:
            List[HistogramDataPoint]: One point per set of attributes.
        """
        merged: Dict[Tuple[Tuple[str, str], ...], HistogramDataPoint] = {}
        for point in points:
            attributes = self._strip(point.attributes)
            key = self._identity(attributes)
            known = merged.get(key)
            if known is None:
                merged[key] = replace(point, attributes=attributes)
                self.logger.debug("Kept a new histogram point.")
            else:
                merged[key] = replace(
                    known,
                    count=known.count + point.count,
                    sum=known.sum + point.sum,
                    bucket_counts=[a + b for a, b in zip(known.bucket_counts, point.bucket_counts)],
                    min=min(known.min, point.min),
                    max=max(known.max, point.max),
                    start_time_unix_nano=min(known.start_time_unix_nano, point.start_time_unix_nano),
                    time_unix_nano=max(known.time_unix_nano, point.time_unix_nano),
                )
                self.logger.debug("Added a histogram point to another.")
        return list(merged.values())

    def _guard(self, metric: Metric) -> Optional[Metric]:
        """Remove the forbidden label from a metric.

        Args:
            metric (Metric): The metric.

        Returns:
            Optional[Metric]: The metric without the label, or None when its kind cannot be merged.
        """
        data = metric.data
        if isinstance(data, Sum):
            return replace(metric, data=replace(data, data_points=self._merge_numbers(data.data_points, False)))
        if isinstance(data, Gauge):
            return replace(metric, data=replace(data, data_points=self._merge_numbers(data.data_points, True)))
        if isinstance(data, Histogram):
            return replace(metric, data=replace(data, data_points=self._merge_histograms(data.data_points)))
        self.logger.warning("Dropped the metric %s, whose kind cannot be merged.", metric.name)
        return None

    ############################
    # Publicly Exposed Methods #
    ############################

    def export(self, metrics_data: MetricsData, timeout_millis: float = 10_000, **kwargs: float) -> MetricExportResult:
        """Export the metrics without the forbidden label.

        Args:
            metrics_data (MetricsData): The metrics to export.
            timeout_millis (float): The time allowed, in milliseconds.
            **kwargs (float): The options of the inner exporter.

        Returns:
            MetricExportResult: The result of the inner exporter.
        """
        resources: List[ResourceMetrics] = []
        for resource_metrics in metrics_data.resource_metrics:
            scopes: List[ScopeMetrics] = []
            for scope_metrics in resource_metrics.scope_metrics:
                guarded = [self._guard(metric) for metric in scope_metrics.metrics]
                kept = [metric for metric in guarded if metric is not None]
                scopes.append(replace(scope_metrics, metrics=kept))
            resources.append(replace(resource_metrics, scope_metrics=scopes))
        self.logger.debug("Exported the metrics of %d resources.", len(resources))
        return self.inner.export(MetricsData(resource_metrics=resources), timeout_millis, **kwargs)

    def force_flush(self, timeout_millis: float = 10_000) -> bool:
        """Flush the inner exporter.

        Args:
            timeout_millis (float): The time allowed, in milliseconds.

        Returns:
            bool: The answer of the inner exporter.
        """
        self.logger.debug("Flushed the label guard.")
        return self.inner.force_flush(timeout_millis)

    def shutdown(self, timeout_millis: float = 30_000, **kwargs: float) -> None:
        """Shut the inner exporter down.

        Args:
            timeout_millis (float): The time allowed, in milliseconds.
            **kwargs (float): The options of the inner exporter.
        """
        self.logger.debug("Shut the label guard down.")
        self.inner.shutdown(timeout_millis, **kwargs)
