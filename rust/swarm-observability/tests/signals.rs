//! Tests of the OpenTelemetry signals of Swarm, with in-memory exporters.

use std::sync::{Arc, Mutex};

use opentelemetry::trace::{SpanContext, SpanId, TraceContextExt, TraceFlags, TraceId, TraceState, Tracer as _};
use opentelemetry::{Context, KeyValue};
use opentelemetry_sdk::error::OTelSdkResult;
use opentelemetry_sdk::metrics::data::{AggregatedMetrics, MetricData};
use opentelemetry_sdk::metrics::InMemoryMetricExporter;
use opentelemetry_sdk::resource::Resource;
use opentelemetry_sdk::trace::{InMemorySpanExporter, SpanData, SpanExporter};
use swarm_observability::{trace_parent, Signals, SignalsConfig};

const SERVICE: &str = "swarm-test";
const CELL: &str = "cell-a";
const ENDPOINT_VARIABLE: &str = "OTEL_EXPORTER_OTLP_ENDPOINT";

fn config() -> SignalsConfig {
    SignalsConfig {
        endpoint: Some("http://127.0.0.1:1".to_string()),
        service_name: SERVICE.to_string(),
        cell: CELL.to_string(),
    }
}

/// A span exporter that keeps the spans and the resource it is given.
#[derive(Clone, Debug, Default)]
struct Recorder {
    spans: Arc<Mutex<Vec<SpanData>>>,
    resource: Arc<Mutex<Option<Resource>>>,
}

impl SpanExporter for Recorder {
    fn export(&self, batch: Vec<SpanData>) -> impl std::future::Future<Output = OTelSdkResult> + Send {
        self.spans.lock().expect("lock").extend(batch);
        std::future::ready(Ok(()))
    }

    fn set_resource(&mut self, resource: &Resource) {
        *self.resource.lock().expect("lock") = Some(resource.clone());
    }
}

fn has_key(attributes: &[KeyValue], key: &str) -> bool {
    attributes.iter().any(|entry| entry.key.as_str() == key)
}

#[test]
fn an_exported_span_has_the_service_name_and_the_cell_in_its_resource() {
    let recorder = Recorder::default();
    let signals = Signals::with_exporters(&config(), recorder.clone(), InMemoryMetricExporter::default())
        .expect("signals start with in-memory exporters");
    signals.tracer().in_span("flight", |_| {});
    signals.shutdown();
    assert_eq!(recorder.spans.lock().expect("lock").len(), 1);
    let resource = recorder.resource.lock().expect("lock").clone().expect("a resource");
    let pairs: Vec<(String, String)> = resource
        .iter()
        .map(|(key, value)| (key.to_string(), value.to_string()))
        .collect();
    assert!(pairs.contains(&("service.name".to_string(), SERVICE.to_string())));
    assert!(pairs.contains(&("cell".to_string(), CELL.to_string())));
}

#[test]
fn a_span_is_exported_without_secrets() {
    let exporter = InMemorySpanExporter::default();
    let signals =
        Signals::with_exporters(&config(), exporter.clone(), InMemoryMetricExporter::default()).expect("signals start");
    let tracer = signals.tracer();
    tracer
        .span_builder("request")
        .with_attributes(vec![
            KeyValue::new("http.request.header.authorization", "Bearer secret"),
            KeyValue::new("user.email", "pilot@example.org"),
            KeyValue::new("mission_id", "m-1"),
        ])
        .start(&tracer);
    signals.shutdown();
    let spans = exporter.get_finished_spans().expect("finished spans");
    assert_eq!(spans.len(), 1);
    assert!(!has_key(&spans[0].attributes, "http.request.header.authorization"));
    assert!(!has_key(&spans[0].attributes, "user.email"));
    assert!(has_key(&spans[0].attributes, "mission_id"));
}

#[test]
fn a_counter_is_exported_with_mission_id_and_without_drone_id() {
    let metrics = InMemoryMetricExporter::default();
    let signals =
        Signals::with_exporters(&config(), InMemorySpanExporter::default(), metrics.clone()).expect("signals start");
    let counter = signals.meter().u64_counter("swarm.commands").build();
    counter.add(
        1,
        &[KeyValue::new("drone_id", "d-1"), KeyValue::new("mission_id", "m-1")],
    );
    signals.shutdown();
    let mut seen = 0;
    for resource_metrics in metrics.get_finished_metrics().expect("finished metrics") {
        for scope in resource_metrics.scope_metrics() {
            for metric in scope.metrics() {
                if let AggregatedMetrics::U64(MetricData::Sum(sum)) = metric.data() {
                    for point in sum.data_points() {
                        let attributes: Vec<KeyValue> = point.attributes().cloned().collect();
                        assert!(has_key(&attributes, "mission_id"));
                        assert!(!has_key(&attributes, "drone_id"));
                        seen += 1;
                    }
                }
            }
        }
    }
    assert!(seen > 0, "no data point was exported");
}

#[test]
fn trace_parent_gives_the_w3c_form_for_a_valid_span() {
    let context = SpanContext::new(
        TraceId::from_hex("0af7651916cd43dd8448eb211c80319c").expect("trace id"),
        SpanId::from_hex("b7ad6b7169203331").expect("span id"),
        TraceFlags::SAMPLED,
        false,
        TraceState::default(),
    );
    let value = trace_parent(&context).expect("a traceparent");
    assert_eq!(value, "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01");
    let lengths: Vec<usize> = value.split('-').map(str::len).collect();
    assert_eq!(lengths, vec![2, 32, 16, 2]);
}

#[test]
fn trace_parent_gives_nothing_for_an_invalid_context() {
    assert!(trace_parent(&SpanContext::empty_context()).is_none());
    assert!(trace_parent(Context::current().span().span_context()).is_none());
}

#[test]
fn from_env_with_no_endpoint_gives_disabled_signals() {
    std::env::remove_var(ENDPOINT_VARIABLE);
    let config = SignalsConfig::from_env(SERVICE);
    assert!(config.endpoint.is_none());
    assert_eq!(config.service_name, SERVICE);
    let signals = Signals::start(&config).expect("disabled signals start");
    assert!(!signals.enabled());
    signals.shutdown();
}
