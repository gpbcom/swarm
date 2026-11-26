from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from math import hypot
from typing import ClassVar, Dict, List, Optional
from uuid import UUID

# First-party imports
from swarm_models.flight.missions.drone_entry import DroneEntry
from swarm_models.flight.missions.mission_entry import MissionEntry
from swarm_models.flight.telemetry.drone_sample import DroneSample
from swarm_models.flight.telemetry.drone_state_catalog import DroneStateCatalog
from swarm_models.telemetry.enums.drone_state import DroneState
from swarm_models.telemetry.squad_frame import SquadFrame
from swarm_models.telemetry.telemetry_frame import TelemetryFrame


class SquadFrameBuilder:
    """Turns the latest samples of the Drones of one Mission into one SquadFrame.

    Attributes:
        mission (MissionEntry): The Mission, whose registry of Drones decides which samples count.
        states (DroneStateCatalog): Maps a MAVLink ``system_status`` to the state of a Drone.
        link_lost_after_ms (int): How long without a frame before a Drone is ``LOST``, in milliseconds.
        drones (Dict[int, DroneEntry]): The Drones of the Mission by system id.
        sequences (Dict[UUID, int]): The sequence number the next frame of each Drone gets.
        logger (Logger): Logger instance.
        US_PER_MS (int): The microseconds in a millisecond.
        MM_PER_M (int): The millimetres in a metre.
        CM_PER_M (int): The centimetres in a metre.
        CDEG_PER_DEG (int): The hundredths of a degree in a degree.
        HDG_UNKNOWN_CDEG (int): The MAVLink heading that means unknown.
        BATTERY_UNKNOWN (int): The MAVLink battery value that means unknown.
        FULL_PCT (float): One hundred percent.
        UNKNOWN_VALUE (float): The battery and heading given when the Drone does not report them.

    Notes:
        - **A Drone appears in a SquadFrame only once its position is known**, and a sample of a system id outside
          the Mission is ignored.
        - The sequence number counts per Drone, from 0, and goes up each time the Drone appears in a build.
    """

    US_PER_MS: ClassVar[int] = 1000
    MM_PER_M: ClassVar[int] = 1000
    CM_PER_M: ClassVar[int] = 100
    CDEG_PER_DEG: ClassVar[int] = 100
    HDG_UNKNOWN_CDEG: ClassVar[int] = 65535
    BATTERY_UNKNOWN: ClassVar[int] = -1
    FULL_PCT: ClassVar[float] = 100.0
    UNKNOWN_VALUE: ClassVar[float] = 0.0

    def __init__(
        self,
        mission: MissionEntry,
        states: DroneStateCatalog,
        link_lost_after_ms: int,
        logger: Optional[Logger] = None,
    ) -> None:
        """Prepare the builder of a Mission.

        Args:
            mission (MissionEntry): The Mission.
            states (DroneStateCatalog): The catalogue of Drone states.
            link_lost_after_ms (int): The silence after which a Drone is lost, in milliseconds.
            logger (Optional[Logger]): Logger instance.
        """
        self.mission = mission
        self.states = states
        self.link_lost_after_ms = link_lost_after_ms
        self.drones: Dict[int, DroneEntry] = {drone.system_id: drone for drone in mission.drones}
        self.sequences: Dict[UUID, int] = {}
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _heading_deg(self, sample: DroneSample) -> float:
        """Give the heading in degrees, or 0.0 when the Drone does not report it.

        Args:
            sample (DroneSample): The sample.

        Returns:
            float: The heading.
        """
        if sample.hdg_cdeg == self.HDG_UNKNOWN_CDEG:
            self.logger.debug("Drone %d reports no heading.", sample.system_id)
            return self.UNKNOWN_VALUE
        return sample.hdg_cdeg / self.CDEG_PER_DEG

    def _battery_pct(self, sample: DroneSample) -> float:
        """Give the battery charge in percent, or 0.0 when the Drone does not report it.

        Args:
            sample (DroneSample): The sample.

        Returns:
            float: The charge.
        """
        if sample.battery_remaining == self.BATTERY_UNKNOWN:
            self.logger.debug("Drone %d reports no battery.", sample.system_id)
            return self.UNKNOWN_VALUE
        return float(sample.battery_remaining)

    def _link_quality_pct(self, sample: DroneSample) -> float:
        """Give the share of received frames in percent, or 100 when none was lost.

        Args:
            sample (DroneSample): The sample.

        Returns:
            float: The quality of the Link.
        """
        total = sample.received + sample.lost
        if total == 0:
            self.logger.debug("Drone %d has counted no frame yet.", sample.system_id)
            return self.FULL_PCT
        return self.FULL_PCT * sample.received / total

    def _state(self, sample: DroneSample, now_us: int) -> DroneState:
        """Give the state of a Drone, ``LOST`` when it has been silent for too long.

        Args:
            sample (DroneSample): The sample.
            now_us (int): The moment of the tick, in microseconds.

        Returns:
            DroneState: The state.
        """
        if now_us - sample.updated_at_us > self.link_lost_after_ms * self.US_PER_MS:
            self.logger.debug("Drone %d has been silent for too long.", sample.system_id)
            return DroneState.LOST
        return self.states.state_of(sample.system_status)

    def _frame(self, drone: DroneEntry, sample: DroneSample, now_us: int) -> TelemetryFrame:
        """Build the frame of one Drone and advance its sequence number.

        Args:
            drone (DroneEntry): The Drone of the Mission.
            sample (DroneSample): Its latest sample.
            now_us (int): The moment of the tick, in microseconds.

        Returns:
            TelemetryFrame: The frame.
        """
        seq = self.sequences.get(drone.drone_id, 0)
        self.sequences[drone.drone_id] = seq + 1
        return TelemetryFrame(
            mission_id=self.mission.mission_id,
            drone_id=drone.drone_id,
            seq=seq,
            t_us=sample.updated_at_us,
            lat_e7=sample.lat_e7,
            lon_e7=sample.lon_e7,
            altitude_m=sample.relative_alt_mm / self.MM_PER_M,
            speed_m_s=hypot(sample.vx_cm_s, sample.vy_cm_s) / self.CM_PER_M,
            heading_deg=self._heading_deg(sample),
            battery_pct=self._battery_pct(sample),
            link_quality_pct=self._link_quality_pct(sample),
            state=self._state(sample, now_us),
        )

    ############################
    # Publicly Exposed Methods #
    ############################

    def build(self, samples: List[DroneSample], now_us: int) -> SquadFrame:
        """Build the SquadFrame of one tick.

        Args:
            samples (List[DroneSample]): The latest sample of each Drone heard from.
            now_us (int): The moment of the tick, in microseconds since the epoch.

        Returns:
            SquadFrame: One frame per Drone of the Mission whose position is known.
        """
        frames: List[TelemetryFrame] = []
        for sample in samples:
            drone = self.drones.get(sample.system_id)
            if drone is None:
                self.logger.debug("Ignored system id %d: not a Drone of the Mission.", sample.system_id)
                continue
            if not sample.has_position:
                self.logger.debug("Skipped Drone %d: no position yet.", sample.system_id)
                continue
            frames.append(self._frame(drone, sample, now_us))
        self.logger.debug("Built a SquadFrame of %d frames.", len(frames))
        return SquadFrame(mission_id=self.mission.mission_id, t_us=now_us, frames=frames)
