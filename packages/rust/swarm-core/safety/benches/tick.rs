//! Benchmark of the safety tick placeholder on 1,000 values.

use std::hint::black_box;

use criterion::{criterion_group, criterion_main, Criterion};
use swarm_core_safety::tick;

fn bench(c: &mut Criterion) {
    let values: Vec<u64> = (0..1000).collect();
    c.bench_function("safety_tick", |b| b.iter(|| tick(black_box(&values))));
}

criterion_group!(benches, bench);
criterion_main!(benches);
