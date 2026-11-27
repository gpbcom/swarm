//! The span exporter that removes secrets and personal data before anything leaves the process.

use std::future::Future;

use opentelemetry::KeyValue;
use opentelemetry_sdk::error::OTelSdkResult;
use opentelemetry_sdk::resource::Resource;
use opentelemetry_sdk::trace::{SpanData, SpanExporter};
use std::time::Duration;

/// The parts of an attribute key that mark its value as a secret or as personal data. A key that contains
/// one of them, in any letter case, is removed.
pub const SENSITIVE_KEYS: [&str; 11] = [
    "authorization",
    "cookie",
    "password",
    "secret",
    "token",
    "credential",
    "api_key",
    "email",
    "phone",
    "enduser",
    "url.query",
];

/// Whether an attribute key marks a secret or personal data (see [`SENSITIVE_KEYS`]).
#[must_use]
pub fn is_sensitive(key: &str) -> bool {
    let key = key.to_ascii_lowercase();
    SENSITIVE_KEYS.iter().any(|part| key.contains(part))
}

/// Remove the sensitive attributes from a list, keeping the order of the others.
fn redact(attributes: &mut Vec<KeyValue>) {
    attributes.retain(|attribute| !is_sensitive(attribute.key.as_str()));
}

/// A span exporter that removes the sensitive attributes of every span, of its events and of its links,
/// then hands the batch to the exporter it wraps.
#[derive(Debug)]
pub struct RedactingExporter<E> {
    inner: E,
    forward_shutdown: bool,
}

impl<E: SpanExporter> RedactingExporter<E> {
    /// Wrap `inner`, which is shut down with the wrapper.
    #[must_use]
    pub fn new(inner: E) -> Self {
        Self {
            inner,
            forward_shutdown: true,
        }
    }

    /// Wrap `inner`, which is never shut down by the wrapper.
    ///
    /// A recording exporter of a test clears what it holds when it is shut down. The test owns it, and reads
    /// it after the signals ended.
    #[must_use]
    pub fn keeping_inner_open(inner: E) -> Self {
        Self {
            inner,
            forward_shutdown: false,
        }
    }
}

impl<E: SpanExporter> SpanExporter for RedactingExporter<E> {
    fn export(&self, mut batch: Vec<SpanData>) -> impl Future<Output = OTelSdkResult> + Send {
        for span in &mut batch {
            redact(&mut span.attributes);
            for event in &mut span.events.events {
                redact(&mut event.attributes);
            }
            for link in &mut span.links.links {
                redact(&mut link.attributes);
            }
        }
        self.inner.export(batch)
    }

    fn shutdown_with_timeout(&self, timeout: Duration) -> OTelSdkResult {
        if self.forward_shutdown {
            self.inner.shutdown_with_timeout(timeout)
        } else {
            Ok(())
        }
    }

    fn force_flush(&self) -> OTelSdkResult {
        self.inner.force_flush()
    }

    fn set_resource(&mut self, resource: &Resource) {
        self.inner.set_resource(resource);
    }
}

#[cfg(test)]
mod tests {
    use super::{is_sensitive, redact};
    use opentelemetry::KeyValue;

    #[test]
    fn the_keys_that_hold_secrets_or_personal_data_are_sensitive() {
        for key in [
            "http.request.header.authorization",
            "Cookie",
            "db.password",
            "client_secret",
            "access_token",
            "aws.credentials",
            "x-api_key",
            "user.email",
            "contact.phone",
            "enduser.id",
            "url.query",
        ] {
            assert!(is_sensitive(key), "{key} must be sensitive");
        }
    }

    #[test]
    fn the_keys_of_the_business_stay() {
        for key in ["mission_id", "drone_id", "operator_id", "http.route"] {
            assert!(!is_sensitive(key), "{key} must stay");
        }
    }

    #[test]
    fn redact_keeps_the_order_of_what_stays() {
        let mut attributes = vec![
            KeyValue::new("a", "1"),
            KeyValue::new("user.email", "x"),
            KeyValue::new("b", "2"),
        ];
        redact(&mut attributes);
        let keys: Vec<&str> = attributes.iter().map(|entry| entry.key.as_str()).collect();
        assert_eq!(keys, vec!["a", "b"]);
    }
}
