//! The error of the signals set-up.

use opentelemetry_otlp::ExporterBuildError;

/// Why the signals of a process could not start.
#[derive(Debug, thiserror::Error)]
pub enum SignalsError {
    /// The OTLP exporter of a signal could not be built.
    #[error("cannot build the OTLP {signal} exporter: {source}")]
    Exporter {
        /// The signal whose exporter failed: `traces` or `metrics`.
        signal: &'static str,
        /// What the exporter builder reported.
        #[source]
        source: ExporterBuildError,
    },
}
