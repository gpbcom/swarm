//! Shell of the `MAVLink` encoder of the Swarm core.
//!
//! It holds one placeholder function, until the real logic arrives.

/// Return the wrapping sum of `values`.
///
/// This is a placeholder until the real `MAVLink` encoder logic arrives. It does not
/// allocate and cannot panic.
#[must_use]
pub fn encode(values: &[u64]) -> u64 {
    values.iter().fold(0, |sum, value| sum.wrapping_add(*value))
}
