//! The OpenTelemetry signals of the Swarm services written in Rust.
//!
//! [`Signals`] sets up the traces and the metrics of one process. The resource of every signal carries
//! `service.name` and `cell`. Spans go through a redacting exporter that removes the attributes that could
//! hold a secret or personal data ([`is_sensitive`]), and metric streams never carry `drone_id`
//! ([`ALLOWED_METRIC_KEYS`]). With no collector endpoint the signals are disabled and export nothing, and a
//! collector that is missing or unreachable never stops the caller: exports fail on their own threads.
//!
//! [`trace_parent`] gives the W3C `traceparent` of a span context.

mod config;
mod error;
mod metric_guard;
mod redaction;
mod signals;

pub use config::SignalsConfig;
pub use error::SignalsError;
pub use metric_guard::ALLOWED_METRIC_KEYS;
pub use redaction::{is_sensitive, RedactingExporter, SENSITIVE_KEYS};
pub use signals::{trace_parent, Signals};
