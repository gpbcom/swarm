//! Integration tests of the route follower of the synthetic drones.

use swarm_synthetic_drones::route::{distance_m, offset, Position, RouteFollower, ARRIVAL_TOLERANCE_M};

const SPEED_M_S: f32 = 10.0;
const DT_S: f32 = 0.05;
const SIDE_M: f32 = 50.0;
const MAX_STEPS: usize = 100_000;

fn origin() -> Position {
    Position {
        lat_e7: 473_977_000,
        lon_e7: 85_456_000,
        altitude_m: 30.0,
    }
}

fn square() -> Vec<Position> {
    let start = origin();
    vec![
        offset(start, SIDE_M, 0.0),
        offset(start, SIDE_M, SIDE_M),
        offset(start, 0.0, SIDE_M),
        offset(start, 0.0, 0.0),
        offset(start, SIDE_M, 0.0),
    ]
}

fn path_length_m(start: Position, waypoints: &[Position]) -> f32 {
    let mut previous = start;
    let mut total = 0.0;
    for waypoint in waypoints {
        total += distance_m(previous, *waypoint);
        previous = *waypoint;
    }
    total
}

/// Runs the follower to the end and returns the reached indexes, the steps taken and the follower.
fn fly(waypoints: &[Position]) -> (Vec<usize>, usize, RouteFollower) {
    let mut follower = RouteFollower::new(origin(), SPEED_M_S);
    follower.set_route(waypoints);
    let mut reached = Vec::new();
    let mut steps = 0;
    while !follower.is_complete() && steps < MAX_STEPS {
        if let Some(index) = follower.step(DT_S) {
            reached.push(index);
        }
        steps += 1;
    }
    (reached, steps, follower)
}

#[test]
fn a_square_route_reaches_every_waypoint_in_order_then_completes() {
    let (reached, _, follower) = fly(&square());
    assert_eq!(reached, vec![0, 1, 2, 3, 4]);
    assert!(follower.is_complete());
}

#[test]
fn the_elapsed_time_is_the_path_length_over_the_speed() {
    let route = square();
    let (_, steps, _) = fly(&route);
    #[allow(clippy::cast_precision_loss)]
    let elapsed_s = steps as f32 * DT_S;
    let expected_s = path_length_m(origin(), &route) / SPEED_M_S;
    assert!(
        (elapsed_s - expected_s).abs() <= expected_s * 0.1,
        "{elapsed_s} s against {expected_s} s"
    );
}

#[test]
fn a_step_between_waypoints_returns_none() {
    let mut follower = RouteFollower::new(origin(), SPEED_M_S);
    follower.set_route(&square());
    assert_eq!(follower.current_index(), Some(0));
    assert_eq!(follower.step(DT_S), None);
    assert_eq!(follower.current_index(), Some(0));
    assert!(!follower.is_complete());
}

#[test]
fn the_final_position_is_within_the_tolerance_of_the_last_waypoint() {
    let route = square();
    let (_, _, follower) = fly(&route);
    let last = route[route.len() - 1];
    assert!(distance_m(follower.position(), last) <= ARRIVAL_TOLERANCE_M);
}

#[test]
fn an_empty_route_is_complete_at_once() {
    let mut follower = RouteFollower::new(origin(), SPEED_M_S);
    follower.set_route(&[]);
    assert!(follower.is_complete());
    assert_eq!(follower.current_index(), None);
    assert_eq!(follower.step(DT_S), None);
}

#[test]
fn offset_and_distance_agree_within_half_a_percent() {
    let moved = offset(origin(), 300.0, 400.0);
    let measured = distance_m(origin(), moved);
    assert!((measured - 500.0).abs() <= 500.0 * 0.005, "{measured} m against 500 m");
}
