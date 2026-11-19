//! Integration tests of the safety tick placeholder.

use swarm_core_safety::tick;

#[test]
fn an_empty_slice_gives_zero() {
    assert_eq!(tick(&[]), 0);
}

#[test]
fn one_two_three_gives_six() {
    assert_eq!(tick(&[1, 2, 3]), 6);
}

#[test]
fn a_sum_that_overflows_wraps_instead_of_panicking() {
    assert_eq!(tick(&[u64::MAX, 1]), 0);
}

#[test]
fn two_calls_on_the_same_values_give_the_sum_of_the_range() {
    let values: Vec<u64> = (0..1000).collect();
    let first = tick(&values);
    let second = tick(&values);
    assert_eq!(first, second);
    assert_eq!(first, (0..1000).sum::<u64>());
}
