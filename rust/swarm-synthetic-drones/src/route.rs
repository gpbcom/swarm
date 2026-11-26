//! Positions on the globe and the follower that flies a route.
//!
//! The maths is a local flat-earth projection around a reference position, with an Earth radius of 6,371,000 m.
//! It is exact enough for the few kilometres a simulated Mission covers.

/// Radius of the Earth, in metres, used by the local projection.
const EARTH_RADIUS_M: f64 = 6_371_000.0;

/// Degrees times ten million per radian, the unit of the `MAVLink` integer coordinates.
const E7_PER_RAD: f64 = 1.0e7 * 180.0 / std::f64::consts::PI;

/// Distance, in metres, under which a waypoint counts as reached.
pub const ARRIVAL_TOLERANCE_M: f32 = 1.0;

/// A position: latitude and longitude in degrees times ten million, and the altitude in metres.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Position {
    /// Latitude in degrees times ten million.
    pub lat_e7: i32,
    /// Longitude in degrees times ten million.
    pub lon_e7: i32,
    /// Altitude in metres.
    pub altitude_m: f32,
}

/// The cosine of the latitude of a reference position, which scales the east axis of the projection.
fn cos_latitude(reference: Position) -> f64 {
    (f64::from(reference.lat_e7) / E7_PER_RAD).cos()
}

/// Local coordinates in metres (north, east, up) of `position` around `reference`.
fn to_local(reference: Position, cos_lat: f64, position: Position) -> [f64; 3] {
    let north_m = (f64::from(position.lat_e7) - f64::from(reference.lat_e7)) / E7_PER_RAD * EARTH_RADIUS_M;
    let east_m = (f64::from(position.lon_e7) - f64::from(reference.lon_e7)) / E7_PER_RAD * EARTH_RADIUS_M * cos_lat;
    let up_m = f64::from(position.altitude_m) - f64::from(reference.altitude_m);
    [north_m, east_m, up_m]
}

/// The position at the local coordinates `local` (north, east, up in metres) around `reference`.
#[allow(clippy::cast_possible_truncation)]
fn from_local(reference: Position, cos_lat: f64, local: [f64; 3]) -> Position {
    let lat_e7 = f64::from(reference.lat_e7) + local[0] / EARTH_RADIUS_M * E7_PER_RAD;
    let lon_e7 = f64::from(reference.lon_e7) + local[1] / (EARTH_RADIUS_M * cos_lat) * E7_PER_RAD;
    Position {
        lat_e7: lat_e7.round() as i32,
        lon_e7: lon_e7.round() as i32,
        altitude_m: (f64::from(reference.altitude_m) + local[2]) as f32,
    }
}

/// The position `north_m` metres north and `east_m` metres east of `origin`, at the same altitude.
#[must_use]
pub fn offset(origin: Position, north_m: f32, east_m: f32) -> Position {
    from_local(
        origin,
        cos_latitude(origin),
        [f64::from(north_m), f64::from(east_m), 0.0],
    )
}

/// The 3D distance in metres from `a` to `b`, in the local flat-earth projection around `a`.
#[must_use]
#[allow(clippy::cast_possible_truncation)]
pub fn distance_m(a: Position, b: Position) -> f32 {
    let [north_m, east_m, up_m] = to_local(a, cos_latitude(a), b);
    north_m.hypot(east_m).hypot(up_m) as f32
}

/// Flies a route at a constant speed, in 3D, one waypoint after the other.
///
/// The follower keeps its state in local coordinates around its start, so that a step is a few float operations.
/// [`RouteFollower::step`] allocates nothing: [`RouteFollower::set_route`] is the only method that stores anything.
#[derive(Clone, Debug)]
pub struct RouteFollower {
    start: Position,
    cos_lat: f64,
    speed_m_s: f64,
    local: [f64; 3],
    waypoints: Vec<[f64; 3]>,
    index: usize,
}

impl RouteFollower {
    /// A follower at `start` that flies at `speed_m_s`, with an empty route.
    #[must_use]
    pub fn new(start: Position, speed_m_s: f32) -> Self {
        Self {
            start,
            cos_lat: cos_latitude(start),
            speed_m_s: f64::from(speed_m_s),
            local: [0.0; 3],
            waypoints: Vec::new(),
            index: 0,
        }
    }

    /// Replaces the route with `waypoints`, copied once, and aims at the first one.
    pub fn set_route(&mut self, waypoints: &[Position]) {
        self.waypoints.clear();
        self.waypoints.reserve(waypoints.len());
        for waypoint in waypoints {
            self.waypoints.push(to_local(self.start, self.cos_lat, *waypoint));
        }
        self.index = 0;
    }

    /// Moves the follower for `dt_s` seconds and returns the index of the waypoint reached in this step, if any.
    ///
    /// At most one waypoint is reached per step, and the rest of the step is dropped. A waypoint is reached when
    /// the step covers the distance left or the distance left is within [`ARRIVAL_TOLERANCE_M`]: the follower then
    /// stands exactly on it.
    pub fn step(&mut self, dt_s: f32) -> Option<usize> {
        let target = *self.waypoints.get(self.index)?;
        let delta = [
            target[0] - self.local[0],
            target[1] - self.local[1],
            target[2] - self.local[2],
        ];
        let remaining_m = delta[0].hypot(delta[1]).hypot(delta[2]);
        let travel_m = self.speed_m_s * f64::from(dt_s);
        if remaining_m <= travel_m.max(f64::from(ARRIVAL_TOLERANCE_M)) {
            self.local = target;
            let reached = self.index;
            self.index += 1;
            return Some(reached);
        }
        if travel_m > 0.0 {
            let ratio = travel_m / remaining_m;
            self.local[0] += delta[0] * ratio;
            self.local[1] += delta[1] * ratio;
            self.local[2] += delta[2] * ratio;
        }
        None
    }

    /// The current position.
    #[must_use]
    pub fn position(&self) -> Position {
        from_local(self.start, self.cos_lat, self.local)
    }

    /// The index of the waypoint the follower flies to, or `None` when the route is complete.
    #[must_use]
    pub fn current_index(&self) -> Option<usize> {
        if self.index < self.waypoints.len() {
            Some(self.index)
        } else {
            None
        }
    }

    /// Whether every waypoint was reached, which is the case at once for an empty route.
    #[must_use]
    pub fn is_complete(&self) -> bool {
        self.index >= self.waypoints.len()
    }
}
