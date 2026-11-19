//! Integration tests of the placeholder `plan` function of `swarm-core-planner`.

use swarm_core_planner::plan;

#[test]
fn an_empty_slice_gives_zero() {
    assert_eq!(plan(&[]), 0);
}

#[test]
fn one_two_and_three_give_six() {
    assert_eq!(plan(&[1, 2, 3]), 6);
}

#[test]
fn a_sum_that_overflows_wraps_to_zero_and_never_panics() {
    assert_eq!(plan(&[u64::MAX, 1]), 0);
}

#[test]
fn two_calls_on_the_same_thousand_values_agree_with_the_plain_sum() {
    let values: Vec<u64> = (0..1000).collect();
    let first = plan(&values);
    let second = plan(&values);
    assert_eq!(first, second);
    assert_eq!(first, (0..1000).sum::<u64>());
}
