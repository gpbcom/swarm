//! `PyO3` bindings of the Swarm core, built into the `swarm_core` wheel by maturin.
//!
//! The module exposes three functions, one per crate of the core, and the classes `LatestFrames` and
//! `DroneSample`. Each one releases the GIL while the Rust code runs, so that other Python threads
//! keep running.

use pyo3::prelude::*;
use pyo3::pybacked::PyBackedBytes;
use swarm_core_mavlink::{DroneSample, LatestFrames};

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

/// What the flight engine knows of one Drone, from its latest frames, as read-only Python values.
#[pyclass(name = "DroneSample", module = "swarm_core", frozen, get_all)]
struct PyDroneSample {
    /// The system id of the Drone.
    system_id: u8,
    /// True once a `GLOBAL_POSITION_INT` has arrived.
    has_position: bool,
    /// Latitude in degrees times 10^7.
    lat_e7: i32,
    /// Longitude in degrees times 10^7.
    lon_e7: i32,
    /// Altitude above the home position in millimetres.
    relative_alt_mm: i32,
    /// Ground speed to the north in centimetres per second.
    vx_cm_s: i16,
    /// Ground speed to the east in centimetres per second.
    vy_cm_s: i16,
    /// Heading in centidegrees.
    hdg_cdeg: u16,
    /// The remaining battery in percent, or -1 until a `SYS_STATUS` arrives.
    battery_remaining: i8,
    /// The base mode of the latest HEARTBEAT.
    base_mode: u8,
    /// The system status of the latest HEARTBEAT.
    system_status: u8,
    /// The number of frames received from this Drone.
    received: u64,
    /// The number of frames lost, counted from the gaps in the sequence numbers.
    lost: u64,
    /// The `now_us` given with the latest frame.
    updated_at_us: u64,
}

impl From<DroneSample> for PyDroneSample {
    fn from(sample: DroneSample) -> Self {
        Self {
            system_id: sample.system_id,
            has_position: sample.has_position,
            lat_e7: sample.lat_e7,
            lon_e7: sample.lon_e7,
            relative_alt_mm: sample.relative_alt_mm,
            vx_cm_s: sample.vx_cm_s,
            vy_cm_s: sample.vy_cm_s,
            hdg_cdeg: sample.hdg_cdeg,
            battery_remaining: sample.battery_remaining,
            base_mode: sample.base_mode,
            system_status: sample.system_status,
            received: sample.received,
            lost: sample.lost,
            updated_at_us: sample.updated_at_us,
        }
    }
}

/// The latest frame of each Drone, kept by the Rust core.
#[pyclass(name = "LatestFrames", module = "swarm_core")]
struct PyLatestFrames {
    inner: LatestFrames,
}

#[pymethods]
impl PyLatestFrames {
    /// Create an empty store.
    #[new]
    fn new() -> Self {
        Self {
            inner: LatestFrames::new(),
        }
    }

    /// Take the well-formed frames of `datagram`, received at `now_us`, with the GIL released.
    ///
    /// Returns how many frames there were. A datagram that is not `bytes` raises `TypeError`.
    fn ingest(&mut self, py: Python<'_>, datagram: PyBackedBytes, now_us: u64) -> usize {
        let inner = &mut self.inner;
        py.detach(move || inner.ingest(&datagram, now_us))
    }

    /// Return the sample of every Drone heard from, ordered by system id.
    fn snapshot(&self) -> Vec<PyDroneSample> {
        self.inner.snapshot().into_iter().map(PyDroneSample::from).collect()
    }
}

/// The `swarm_core` Python module: the three functions and the two classes of the Rust core.
///
/// # Errors
///
/// Returns an error when a function cannot be added to the module.
#[pymodule]
fn swarm_core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(safety_tick, module)?)?;
    module.add_function(wrap_pyfunction!(planner_plan, module)?)?;
    module.add_function(wrap_pyfunction!(mavlink_encode, module)?)?;
    module.add_class::<PyLatestFrames>()?;
    module.add_class::<PyDroneSample>()?;
    Ok(())
}
