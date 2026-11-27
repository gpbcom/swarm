//! The configuration of the signals, read from the standard OpenTelemetry environment.

/// The environment entry that names the collector, as the OpenTelemetry specification does.
const ENDPOINT_VARIABLE: &str = "OTEL_EXPORTER_OTLP_ENDPOINT";
/// The environment entry that holds the resource attributes, `key=value` pairs separated by commas.
const RESOURCE_VARIABLE: &str = "OTEL_RESOURCE_ATTRIBUTES";
/// The key of the cell in the resource attributes.
const CELL_KEY: &str = "cell";
/// The cell of a process whose resource attributes name none.
const DEFAULT_CELL: &str = "local";

/// What the signals of one process need to start.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct SignalsConfig {
    /// The base URL of the OTLP/HTTP collector, or None to disable the signals.
    pub endpoint: Option<String>,
    /// The `service.name` of the resource.
    pub service_name: String,
    /// The `cell` of the resource.
    pub cell: String,
}

impl SignalsConfig {
    /// Read the configuration of `service_name` from `OTEL_EXPORTER_OTLP_ENDPOINT` and the `cell` entry of
    /// `OTEL_RESOURCE_ATTRIBUTES` (`local` when it names none).
    ///
    /// An empty or missing endpoint disables the signals.
    #[must_use]
    pub fn from_env(service_name: &str) -> Self {
        let endpoint = std::env::var(ENDPOINT_VARIABLE).ok();
        let attributes = std::env::var(RESOURCE_VARIABLE).ok();
        Self::from_values(service_name, endpoint.as_deref(), attributes.as_deref())
    }

    /// Build the configuration from the values of the two environment entries.
    #[must_use]
    pub fn from_values(service_name: &str, endpoint: Option<&str>, attributes: Option<&str>) -> Self {
        let endpoint = endpoint
            .map(str::trim)
            .filter(|value| !value.is_empty())
            .map(str::to_string);
        let cell = attributes
            .and_then(Self::cell_of)
            .unwrap_or_else(|| DEFAULT_CELL.to_string());
        Self {
            endpoint,
            service_name: service_name.to_string(),
            cell,
        }
    }

    /// The value of the `cell` pair in a list of resource attributes, if there is a non-empty one.
    fn cell_of(attributes: &str) -> Option<String> {
        attributes
            .split(',')
            .filter_map(|pair| pair.split_once('='))
            .find(|(key, _)| key.trim() == CELL_KEY)
            .map(|(_, value)| value.trim())
            .filter(|value| !value.is_empty())
            .map(str::to_string)
    }
}

#[cfg(test)]
mod tests {
    use super::SignalsConfig;

    #[test]
    fn the_cell_is_read_among_the_resource_attributes() {
        let config = SignalsConfig::from_values("svc", None, Some("deployment.environment=dev, cell = cell-a ,x=y"));
        assert_eq!(config.cell, "cell-a");
    }

    #[test]
    fn the_cell_defaults_to_local() {
        assert_eq!(SignalsConfig::from_values("svc", None, None).cell, "local");
        assert_eq!(SignalsConfig::from_values("svc", None, Some("cell=")).cell, "local");
    }

    #[test]
    fn an_empty_endpoint_disables_the_signals() {
        assert!(SignalsConfig::from_values("svc", Some("  "), None).endpoint.is_none());
        let config = SignalsConfig::from_values("svc", Some(" http://collector:4318 "), None);
        assert_eq!(config.endpoint.as_deref(), Some("http://collector:4318"));
    }
}
