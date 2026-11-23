//! Benchmark of one step of 1,000 route followers on a square.

use std::hint::black_box;

use criterion::{criterion_group, criterion_main, Criterion};
use swarm_synthetic_drones::route::{offset, Position, RouteFollower};

const FOLLOWERS: usize = 1000;
const SPEED_M_S: f32 = 10.0;
const DT_S: f32 = 0.05;
const SIDE_M: f32 = 100.0;

fn square(start: Position) -> Vec<Position> {
    vec![
        offset(start, SIDE_M, 0.0),
        offset(start, SIDE_M, SIDE_M),
        offset(start, 0.0, SIDE_M),
        offset(start, 0.0, 0.0),
    ]
}

fn bench(c: &mut Criterion) {
    let start = Position {
        lat_e7: 473_977_000,
        lon_e7: 85_456_000,
        altitude_m: 30.0,
    };
    let route = square(start);
    let mut followers: Vec<RouteFollower> = (0..FOLLOWERS)
        .map(|_| {
            let mut follower = RouteFollower::new(start, SPEED_M_S);
            follower.set_route(&route);
            follower
        })
        .collect();
    c.bench_function("route_follower_step_1000", |b| {
        b.iter(|| {
            for follower in &mut followers {
                if follower.is_complete() {
                    follower.set_route(&route);
                }
                black_box(follower.step(black_box(DT_S)));
            }
        });
    });
}

criterion_group!(benches, bench);
criterion_main!(benches);
