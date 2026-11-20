//! `PyO3` bindings of the Swarm core, built into the `swarm_core` wheel by maturin.
//!
//! The module exposes three functions, one per crate of the core. Each one releases the GIL
//! while the Rust code runs, so that other Python threads keep running.

use pyo3::prelude::*;

/// Run the safety tick of the Rust core on `values`, with the GIL released.
///
/// A value that is not an integer in the range of `u64` raises `TypeError` or `OverflowError`
/// through `PyO3`'s extraction.
#[pyfunction]
fn safety_tick(py: Python<'_>, values: Vec<u64>) -> u64 {
    py.detach(move || swarm_core_safety::tick(&values))
}

/// Run the planner of the Rust core on `values`, with the GIL released.
///
/// A value that is not an integer in the range of `u64` raises `TypeError` or `OverflowError`
/// through `PyO3`'s extraction.
#[pyfunction]
fn planner_plan(py: Python<'_>, values: Vec<u64>) -> u64 {
    py.detach(move || swarm_core_planner::plan(&values))
}

/// Run the `MAVLink` encoder of the Rust core on `values`, with the GIL released.
///
/// A value that is not an integer in the range of `u64` raises `TypeError` or `OverflowError`
/// through `PyO3`'s extraction.
#[pyfunction]
fn mavlink_encode(py: Python<'_>, values: Vec<u64>) -> u64 {
    py.detach(move || swarm_core_mavlink::encode(&values))
}

/// The `swarm_core` Python module: the three functions of the Rust core.
///
/// # Errors
///
/// Returns an error when a function cannot be added to the module.
#[pymodule]
fn swarm_core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(safety_tick, module)?)?;
    module.add_function(wrap_pyfunction!(planner_plan, module)?)?;
    module.add_function(wrap_pyfunction!(mavlink_encode, module)?)?;
    Ok(())
}
