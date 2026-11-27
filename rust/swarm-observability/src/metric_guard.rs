//! The view that keeps `drone_id`, and every other high-cardinality label, off the metric streams.

use opentelemetry::Key;
use opentelemetry_sdk::metrics::{Instrument, Stream};

/// The only attribute keys a metric stream keeps. Anything else, `drone_id` first, is dropped before the
/// measurements are aggregated, so that the series of a Squad never multiply by its Drones.
pub const ALLOWED_METRIC_KEYS: [&str; 3] = ["operator_id", "mission_id", "cell"];

/// The view of every instrument: its stream keeps the [`ALLOWED_METRIC_KEYS`] and nothing else.
///
/// The name, the unit and the aggregation of the instrument are left as they are.
pub(crate) fn only_allowed_keys(_instrument: &Instrument) -> Option<Stream> {
    Stream::builder()
        .with_allowed_attribute_keys(ALLOWED_METRIC_KEYS.iter().map(|key| Key::from_static_str(key)))
        .build()
        .ok()
}

#[cfg(test)]
mod tests {
    use super::ALLOWED_METRIC_KEYS;

    #[test]
    fn drone_id_is_never_allowed() {
        assert!(!ALLOWED_METRIC_KEYS.contains(&"drone_id"));
    }
}
