//! Benchmark of the planner placeholder on 1,000 values.

use std::hint::black_box;

use criterion::{criterion_group, criterion_main, Criterion};
use swarm_core_planner::plan;

fn bench(c: &mut Criterion) {
    let values: Vec<u64> = (0..1000).collect();
    c.bench_function("planner_plan", |b| b.iter(|| plan(black_box(&values))));
}

criterion_group!(benches, bench);
criterion_main!(benches);
