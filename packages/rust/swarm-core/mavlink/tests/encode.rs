//! Integration tests of `swarm_core_mavlink::encode`, the placeholder wrapping sum.

use swarm_core_mavlink::encode;

#[test]
fn an_empty_slice_encodes_to_zero() {
    assert_eq!(encode(&[]), 0);
}

#[test]
fn one_two_three_encodes_to_six() {
    assert_eq!(encode(&[1, 2, 3]), 6);
}

#[test]
fn the_sum_wraps_instead_of_panicking() {
    assert_eq!(encode(&[u64::MAX, 1]), 0);
}

#[test]
fn two_calls_on_the_same_values_give_the_same_sum() {
    let values: Vec<u64> = (0..1000).collect();
    let first = encode(&values);
    let second = encode(&values);
    assert_eq!(first, second);
    assert_eq!(first, (0..1000u64).sum::<u64>());
}
