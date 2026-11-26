//! The `MAVLink` reader of the Swarm core.
//!
//! [`decode`] reads the `MAVLink` 2 frames of a datagram, and [`LatestFrames`] keeps the latest frame of
//! each Drone, so that the flight engine never waits for a slow Drone. [`encode`] is a placeholder until
//! the real encoder arrives.

mod frame;
mod latest_frames;

pub use frame::{decode, Decoded, Frame, Message};
pub use latest_frames::{DroneSample, LatestFrames};

/// Return the wrapping sum of `values`.
///
/// This is a placeholder until the real `MAVLink` encoder logic arrives. It does not
/// allocate and cannot panic.
#[must_use]
pub fn encode(values: &[u64]) -> u64 {
    values.iter().fold(0, |sum, value| sum.wrapping_add(*value))
}
