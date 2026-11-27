//! The Swarm models as Rust structs.
//!
//! The types are generated from the JSON Schema bundle of the Pydantic models, so that Pydantic stays the single
//! source. Never edit `generated.rs` by hand: run `cargo run -p swarm-models-codegen` to write it again.

#[allow(clippy::all, clippy::pedantic, missing_docs)]
#[rustfmt::skip]
mod generated;

pub use generated::{
    Actor, ActorKind, Anchoring, CellAssignment, Command, CommandKind, CommandLane, Deployment, DroneState, Event,
    JsonValue, Jurisdiction, Language, LiveOperation, LiveRate, LiveSubscription, LlmProvider, Operator, Person, Role,
    RoleName, SquadFrame, TelemetryFrame,
};
