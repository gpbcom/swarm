//! Synthetic Drones of the Swarm simulator.
//!
//! Each synthetic Drone follows a route and speaks `MAVLink`, so that thousands of them can run on one node.
//! The [`route`] module holds the positions and the route follower, which never allocates while it steps.
//! The [`drone`] module holds the `MAVLink` state machine of one Drone.
//! The [`link`] module holds the UDP runtime: a fleet of Drones, one socket each.

pub mod drone;
pub mod link;
pub mod route;
