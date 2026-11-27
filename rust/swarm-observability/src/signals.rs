//! The traces and the metrics of one process.

use opentelemetry::metrics::{Meter, MeterProvider as _};
use opentelemetry::trace::{SpanContext, TracerProvider as _};
use opentelemetry::{InstrumentationScope, KeyValue};
use opentelemetry_otlp::{MetricExporter, Protocol, SpanExporter as OtlpSpanExporter, WithExportConfig};
use opentelemetry_sdk::metrics::exporter::PushMetricExporter;
use opentelemetry_sdk::metrics::{MeterProviderBuilder, SdkMeterProvider};
use opentelemetry_sdk::resource::Resource;
use opentelemetry_sdk::trace::{SdkTracer, SdkTracerProvider, SpanExporter, TracerProviderBuilder};

use crate::config::SignalsConfig;
use crate::error::SignalsError;
use crate::metric_guard::only_allowed_keys;
use crate::redaction::RedactingExporter;

/// The path of the traces under the base URL of the collector.
const TRACES_PATH: &str = "/v1/traces";
/// The path of the metrics under the base URL of the collector.
const METRICS_PATH: &str = "/v1/metrics";
/// The `service.name` attribute of the resource.
const SERVICE_NAME_KEY: &str = "service.name";
/// The `cell` attribute of the resource.
const CELL_KEY: &str = "cell";
/// The version of the W3C `traceparent` header this crate writes.
const TRACE_PARENT_VERSION: &str = "00";

/// The traces and the metrics of one process, to start once and to shut down before it ends.
#[derive(Debug)]
pub struct Signals {
    tracer_provider: SdkTracerProvider,
    meter_provider: SdkMeterProvider,
    service_name: String,
    enabled: bool,
}

impl Signals {
    /// Start the signals of `config`.
    ///
    /// With no endpoint the signals are disabled: spans and measurements are accepted and dropped, nothing is
    /// exported and no thread starts. With an endpoint, spans and metrics go as OTLP/HTTP protobuf to
    /// `<endpoint>/v1/traces` and `<endpoint>/v1/metrics`, from background threads, so that a collector that
    /// is missing or slow never blocks the caller.
    ///
    /// # Errors
    ///
    /// Returns [`SignalsError::Exporter`] when an OTLP exporter cannot be built.
    pub fn start(config: &SignalsConfig) -> Result<Self, SignalsError> {
        let resource = Self::resource(config);
        let Some(endpoint) = config.endpoint.as_deref() else {
            return Ok(Self::assemble(
                config,
                Self::tracer_builder(&resource),
                Self::meter_builder(&resource),
                false,
            ));
        };
        let base = endpoint.trim_end_matches('/');
        let spans = OtlpSpanExporter::builder()
            .with_http()
            .with_protocol(Protocol::HttpBinary)
            .with_endpoint(format!("{base}{TRACES_PATH}"))
            .build()
            .map_err(|source| SignalsError::Exporter {
                signal: "traces",
                source,
            })?;
        let metrics = MetricExporter::builder()
            .with_http()
            .with_protocol(Protocol::HttpBinary)
            .with_endpoint(format!("{base}{METRICS_PATH}"))
            .build()
            .map_err(|source| SignalsError::Exporter {
                signal: "metrics",
                source,
            })?;
        let tracers = Self::tracer_builder(&resource).with_batch_exporter(RedactingExporter::new(spans));
        let meters = Self::meter_builder(&resource).with_periodic_exporter(metrics);
        Ok(Self::assemble(config, tracers, meters, true))
    }

    /// Start the signals of `config` with the given exporters instead of OTLP, for tests.
    ///
    /// Spans reach `spans` through the redacting exporter, one by one as they end, and `spans` is not shut
    /// down with the signals, so that a test reads it afterwards. Measurements reach `metrics` when the
    /// signals shut down.
    ///
    /// # Errors
    ///
    /// Never fails today. The result keeps the signature of [`Signals::start`].
    pub fn with_exporters<S, M>(config: &SignalsConfig, spans: S, metrics: M) -> Result<Self, SignalsError>
    where
        S: SpanExporter + 'static,
        M: PushMetricExporter,
    {
        let resource = Self::resource(config);
        let tracers =
            Self::tracer_builder(&resource).with_simple_exporter(RedactingExporter::keeping_inner_open(spans));
        let meters = Self::meter_builder(&resource).with_periodic_exporter(metrics);
        Ok(Self::assemble(config, tracers, meters, true))
    }

    /// Whether the signals export anything: false when no endpoint was configured.
    #[must_use]
    pub fn enabled(&self) -> bool {
        self.enabled
    }

    /// A tracer of this process, named after its service.
    #[must_use]
    pub fn tracer(&self) -> SdkTracer {
        self.tracer_provider.tracer_with_scope(self.scope())
    }

    /// A meter of this process, named after its service.
    ///
    /// The streams of its instruments keep only the keys of [`crate::ALLOWED_METRIC_KEYS`].
    #[must_use]
    pub fn meter(&self) -> Meter {
        self.meter_provider.meter_with_scope(self.scope())
    }

    /// Export what is still buffered, then stop the signals.
    ///
    /// A failure to export is dropped: the end of a process never waits for, or fails because of, a
    /// collector. A second call does nothing.
    pub fn shutdown(&self) {
        let _ = self.tracer_provider.shutdown();
        let _ = self.meter_provider.shutdown();
    }

    /// The instrumentation scope of the tracers and meters.
    fn scope(&self) -> InstrumentationScope {
        InstrumentationScope::builder(self.service_name.clone()).build()
    }

    /// The resource of every signal: `service.name` and `cell`.
    fn resource(config: &SignalsConfig) -> Resource {
        Resource::builder_empty()
            .with_attributes([
                KeyValue::new(SERVICE_NAME_KEY, config.service_name.clone()),
                KeyValue::new(CELL_KEY, config.cell.clone()),
            ])
            .build()
    }

    /// A tracer provider builder with the resource and no exporter.
    fn tracer_builder(resource: &Resource) -> TracerProviderBuilder {
        SdkTracerProvider::builder().with_resource(resource.clone())
    }

    /// A meter provider builder with the resource, the guard against `drone_id` and no exporter.
    fn meter_builder(resource: &Resource) -> MeterProviderBuilder {
        SdkMeterProvider::builder()
            .with_resource(resource.clone())
            .with_view(only_allowed_keys)
    }

    /// Build the providers.
    fn assemble(
        config: &SignalsConfig,
        tracers: TracerProviderBuilder,
        meters: MeterProviderBuilder,
        enabled: bool,
    ) -> Self {
        Self {
            tracer_provider: tracers.build(),
            meter_provider: meters.build(),
            service_name: config.service_name.clone(),
            enabled,
        }
    }
}

/// The W3C `traceparent` of a span context, `00-<trace id>-<span id>-<flags>`, or None when the context is
/// not valid.
#[must_use]
pub fn trace_parent(context: &SpanContext) -> Option<String> {
    if !context.is_valid() {
        return None;
    }
    Some(format!(
        "{TRACE_PARENT_VERSION}-{}-{}-{:02x}",
        context.trace_id(),
        context.span_id(),
        context.trace_flags().to_u8()
    ))
}
