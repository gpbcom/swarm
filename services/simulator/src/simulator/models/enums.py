from __future__ import annotations

# Standard library imports
from enum import StrEnum, unique


@unique
class SimulatedDroneKind(StrEnum):
    """The kinds of simulated drone.

    Attributes:
        SYNTHETIC: A drone that a built-in program flies.
        PX4_SITL: A PX4 software-in-the-loop drone.
    """

    SYNTHETIC = "synthetic"
    PX4_SITL = "px4_sitl"


@unique
class FlightLogEntryKind(StrEnum):
    """The kinds of entry of a flight log.

    Attributes:
        ROUTE_UPLOADED: A route was uploaded to the drone.
        ARMED: The drone was armed.
        ROUTE_STARTED: The drone started its route.
        WAYPOINT_REACHED: The drone reached a waypoint.
        ROUTE_COMPLETED: The drone completed its route.
        ROUTE_FAILED: The route failed.
        COMMAND_ACCEPTED: A command was accepted.
        COMMAND_REFUSED: A command was refused.
    """

    ROUTE_UPLOADED = "route_uploaded"
    ARMED = "armed"
    ROUTE_STARTED = "route_started"
    WAYPOINT_REACHED = "waypoint_reached"
    ROUTE_COMPLETED = "route_completed"
    ROUTE_FAILED = "route_failed"
    COMMAND_ACCEPTED = "command_accepted"
    COMMAND_REFUSED = "command_refused"


@unique
class CommandVerdict(StrEnum):
    """The verdict on a command.

    Attributes:
        ACCEPTED: The drone accepted the command.
        REFUSED: The command was refused.
    """

    ACCEPTED = "accepted"
    REFUSED = "refused"


@unique
class SimulatorCommandName(StrEnum):
    """The commands of the simulator's command line.

    Attributes:
        SERVE: Serve the commands of a Mission.
        FLY: Fly a route once.
    """

    SERVE = "serve"
    FLY = "fly"
