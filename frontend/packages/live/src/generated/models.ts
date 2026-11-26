/* eslint-disable */
/**
 * This file was generated from swarm_models.schema.json by scripts/generate.ts.
 * Do not edit it by hand. Run pnpm --filter ./frontend/packages/live run generate.
 */

/**
 * The name of the agent, for an agent.
 */
export type AgentName = string | null;
/**
 * Whether the author is a person, a Swarm agent or an outside agent.
 */
export type ActorKind = "person" | "swarm_agent" | "outside_agent";
/**
 * The person who is the author, or the person the agent acts for.
 */
export type PersonId = string | null;
/**
 * The kind of the author of an event.
 *
 * Attributes:
 *     PERSON (str): A person acting directly.
 *     SWARM_AGENT (str): A Swarm agent, which may act for a person.
 *     OUTSIDE_AGENT (str): An outside agent, which always acts for a person.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "ActorKind".
 */
export type ActorKind1 = "person" | "swarm_agent" | "outside_agent";
/**
 * The moment of the assignment, in UTC.
 */
export type AssignedAt = string;
/**
 * The name of the cell.
 */
export type Cell = string;
/**
 * The version 7 identifier of the operator.
 */
export type OperatorId = string;
/**
 * The Drone targeted, or none for the whole Squad.
 */
export type DroneId = string | null;
/**
 * The version 7 identifier of the command.
 */
export type Id = string;
/**
 * Who issued the command.
 */
export type IssuedBy = string;
/**
 * What the command asks.
 */
export type CommandKind = "hold" | "abort" | "return_home" | "manual_control";
/**
 * The lane the command travels in.
 */
export type CommandLane = "safety" | "normal";
/**
 * The Mission the command belongs to.
 */
export type MissionId = string;
/**
 * What a command asks a Drone or a Squad to do.
 *
 * Attributes:
 *     HOLD (str): Hold the position.
 *     ABORT (str): Abort the Mission.
 *     RETURN_HOME (str): Return home.
 *     MANUAL_CONTROL (str): Hand the control to the Operator.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "CommandKind".
 */
export type CommandKind1 = "hold" | "abort" | "return_home" | "manual_control";
/**
 * The lane a command travels in.
 *
 * Attributes:
 *     SAFETY (str): The lane that always jumps the queue.
 *     NORMAL (str): The lane of every other command.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "CommandLane".
 */
export type CommandLane1 = "safety" | "normal";
/**
 * The state of a Drone, with the names of the glossary.
 *
 * Attributes:
 *     READY (str): The Drone is airworthy, charged and available for a Squad.
 *     GROUNDED (str): The Drone may not fly.
 *     AIRBORNE (str): The Drone is flying its part of a Mission.
 *     RETURNING (str): The Drone is flying back to its take-off point or its Dock.
 *     LANDED (str): The Drone is on the ground after a flight.
 *     LOST (str): Ground control has no Link to the Drone, through any path.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "DroneState".
 */
export type DroneState = "ready" | "grounded" | "airborne" | "returning" | "landed" | "lost";
/**
 * The identifier, a version 7 UUID.
 */
export type Id1 = string;
/**
 * The Mission the event is about, none for a fleet event.
 */
export type MissionId1 = string | null;
/**
 * When it happened, in UTC with microseconds.
 */
export type OccurredAt = string;
/**
 * The Operator the event belongs to.
 */
export type OperatorId1 = string;
/**
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "JsonValue".
 */
export type JsonValue = unknown;
/**
 * The type, lower case words separated by dots.
 */
export type Type = string;
/**
 * The version of the type.
 */
export type Version = number;
/**
 * A language in which Swarm shows its screens.
 *
 * Attributes:
 *     ENGLISH: English, the default language.
 *     FRENCH: French.
 *     GERMAN: German.
 *     SPANISH: Spanish.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "Language".
 */
export type Language = "en" | "fr" | "de" | "es";
/**
 * An operation a client asks of the live WebSocket.
 *
 * Attributes:
 *     SUBSCRIBE: Subscribe to a topic.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "LiveOperation".
 */
export type LiveOperation = "subscribe";
/**
 * How often a subscriber receives frames.
 *
 * Attributes:
 *     FULL: Every frame, at the rate of the source.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "LiveRate".
 */
export type LiveRate = "full";
/**
 * What the client asks.
 */
export type LiveOperation1 = "subscribe";
/**
 * How often frames are sent.
 */
export type LiveRate1 = "full";
/**
 * The topic followed, mission/<version 7 UUID>/<kind>.
 */
export type Topic = string;
/**
 * The version 7 identifier of the operator.
 */
export type Id2 = string;
/**
 * The name of the operator.
 */
export type Name = string;
/**
 * The email address of the person.
 */
export type Email = string;
/**
 * The version 7 identifier of the person.
 */
export type Id3 = string;
/**
 * The language of the screens the person sees.
 */
export type Language1 = "en" | "fr" | "de" | "es";
/**
 * The full name of the person.
 */
export type Name1 = string;
/**
 * The Operator the person belongs to, if any.
 */
export type OperatorId2 = string | null;
/**
 * The role.
 */
export type RoleName =
  "pilot" | "mission_planner" | "fleet_maintainer" | "instructor" | "client" | "site_agent" | "swarm_administrator";
/**
 * The Operator the role applies to, if any.
 */
export type OperatorId3 = string | null;
/**
 * The version 7 identifier of the person.
 */
export type PersonId1 = string;
/**
 * The seven roles a person can hold.
 *
 * Attributes:
 *     PILOT (str): Flies Missions.
 *     MISSION_PLANNER (str): Designs Missions.
 *     FLEET_MAINTAINER (str): Maintains the Drones of an Operator.
 *     INSTRUCTOR (str): Instructs the people of an Operator.
 *     CLIENT (str): Orders and receives Deliverables.
 *     SITE_AGENT (str): Acts on a site for an Operator.
 *     SWARM_ADMINISTRATOR (str): Administers Swarm, with no access to the data of Operators.
 *
 * Notes:
 *     **Every role except ``SWARM_ADMINISTRATOR`` belongs to one Operator**, and a Swarm administrator belongs to
 *     none.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "RoleName".
 */
export type RoleName1 =
  "pilot" | "mission_planner" | "fleet_maintainer" | "instructor" | "client" | "site_agent" | "swarm_administrator";
/**
 * The altitude, in metres.
 */
export type AltitudeM = number;
/**
 * The battery charge, in percent.
 */
export type BatteryPct = number;
/**
 * The Drone that sent the frame.
 */
export type DroneId1 = string;
/**
 * The heading, in degrees from north.
 */
export type HeadingDeg = number;
/**
 * The latitude in degrees multiplied by 1e7.
 */
export type LatE7 = number;
/**
 * The quality of the Link, in percent.
 */
export type LinkQualityPct = number;
/**
 * The longitude in degrees multiplied by 1e7.
 */
export type LonE7 = number;
/**
 * The Mission the frame belongs to.
 */
export type MissionId2 = string;
/**
 * The sequence number per Drone, which detects gaps.
 */
export type Seq = number;
/**
 * The speed, in metres per second.
 */
export type SpeedMS = number;
/**
 * The state of the Drone.
 */
export type DroneState1 = "ready" | "grounded" | "airborne" | "returning" | "landed" | "lost";
/**
 * The moment of the frame, in microseconds since the epoch.
 */
export type TUs = number;
/**
 * One frame per Drone.
 */
export type Frames = TelemetryFrame[];
/**
 * The Mission of the frames.
 */
export type MissionId3 = string;
/**
 * The moment of the tick, in microseconds since the epoch.
 */
export type TUs1 = number;

export interface SwarmModels {
  [k: string]: unknown;
}
/**
 * The author of an event.
 *
 * Attributes:
 *     model_config (ConfigDict): Forbids unknown keys and freezes the actor.
 *     kind (ActorKind): Whether the author is a person, a Swarm agent or an outside agent.
 *     person_id (Optional[UUID]): The person, who is the author or the person the agent acts for.
 *     agent_name (Optional[str]): The name of the agent, for an agent.
 *
 * Notes:
 *     - A person has a ``person_id`` and no ``agent_name``.
 *     - A Swarm agent has an ``agent_name`` and may act for a person.
 *     - **An outside agent always has both**, because it never acts without the person it acts for.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "Actor".
 */
export interface Actor {
  agent_name?: AgentName;
  kind: ActorKind;
  person_id?: PersonId;
}
/**
 * The cell an operator belongs to, and since when.
 *
 * Attributes:
 *     model_config (ConfigDict): Forbids unknown keys.
 *     operator_id (UUID): The version 7 identifier of the operator.
 *     cell (str): The name of the cell.
 *     assigned_at (datetime): The moment of the assignment, in UTC.
 *
 * Notes:
 *     - An operator lives in exactly one cell.
 *     - No field has a default, so ``None`` is refused.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "CellAssignment".
 */
export interface CellAssignment {
  assigned_at: AssignedAt;
  cell: Cell;
  operator_id: OperatorId;
}
/**
 * An order given to one Drone or to the whole Squad, in a Mission.
 *
 * Attributes:
 *     model_config (ConfigDict): Forbids unknown keys and freezes the command.
 *     SAFETY_KINDS (ClassVar[FrozenSet[CommandKind]]): The kinds that travel in the safety lane.
 *     id (UUID): The version 7 identifier of the command.
 *     mission_id (UUID): The Mission the command belongs to.
 *     drone_id (Optional[UUID]): The Drone targeted, or ``None`` for the whole Squad.
 *     kind (CommandKind): What the command asks.
 *     issued_by (UUID): Who issued the command.
 *     lane (CommandLane): The lane the command travels in.
 *
 * Notes:
 *     - The safety lane always jumps the queue, and the normal lane is for the rest.
 *     - **A safety kind on the normal lane is refused**, so that a safety order never waits.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "Command".
 */
export interface Command {
  drone_id?: DroneId;
  id: Id;
  issued_by: IssuedBy;
  kind: CommandKind;
  lane: CommandLane;
  mission_id: MissionId;
}
/**
 * The envelope of every change published by Swarm.
 *
 * Attributes:
 *     model_config (ConfigDict): Forbids unknown keys and freezes the event.
 *     TYPE_PATTERN (ClassVar[str]): The shape of a type, such as ``mission.planned``.
 *     VERSION_MIN (ClassVar[int]): The smallest version of an event.
 *     id (UUID): The identifier, a version 7 UUID.
 *     type (str): The type, lower case words separated by dots.
 *     version (int): The version of the type.
 *     operator_id (UUID): The Operator the event belongs to.
 *     mission_id (Optional[UUID]): The Mission the event is about, none for a fleet event.
 *     occurred_at (datetime): When it happened, in UTC with microseconds.
 *     actor (Actor): Who did it.
 *     payload (Dict[str, JsonValue]): The model that changed.
 *
 * Notes:
 *     - **The event is frozen**, because a published event is never edited.
 *     - An ``actor`` given as a mapping becomes an ``Actor``, and the errors of the actor are raised unchanged.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "Event".
 */
export interface Event {
  actor: Actor1;
  id: Id1;
  mission_id?: MissionId1;
  occurred_at: OccurredAt;
  operator_id: OperatorId1;
  payload: Payload;
  type: Type;
  version?: Version;
}
/**
 * Who did it.
 */
export interface Actor1 {
  agent_name?: AgentName;
  kind: ActorKind;
  person_id?: PersonId;
}
/**
 * The model that changed.
 */
export interface Payload {
  [k: string]: JsonValue;
}
/**
 * The message a client sends on the live WebSocket to follow a topic.
 *
 * Attributes:
 *     model_config (ConfigDict): Forbids unknown keys and freezes the subscription.
 *     TOPIC_PREFIX (ClassVar[str]): The first part of every topic.
 *     TOPIC_SEPARATOR (ClassVar[str]): The separator between the parts of a topic.
 *     TOPIC_PATTERN (ClassVar[Pattern[str]]): The shape of a topic, ``mission/<id>/<kind>``.
 *     op (LiveOperation): What the client asks.
 *     topic (str): The topic followed, ``mission/<version 7 UUID>/<kind>``.
 *     rate (LiveRate): How often frames are sent. Defaults to full.
 *
 * Notes:
 *     - The topic stays a string on the wire,
 *       and ``mission()`` and ``kind()`` read its parts.
 *     - **A mission identifier that is not a version 7 UUID is refused.**
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "LiveSubscription".
 */
export interface LiveSubscription {
  op: LiveOperation1;
  rate?: LiveRate1;
  topic: Topic;
}
/**
 * A person who pilots drones, global to every cell.
 *
 * Attributes:
 *     model_config (ConfigDict): Forbids unknown keys.
 *     id (UUID): The version 7 identifier of the operator.
 *     name (str): The name of the operator.
 *
 * Notes:
 *     - An operator lives in exactly one cell, given by its ``CellAssignment``.
 *     - No field has a default, so ``None`` is refused.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "Operator".
 */
export interface Operator {
  id: Id2;
  name: Name;
}
/**
 * A person known to Swarm.
 *
 * Attributes:
 *     model_config (ConfigDict): Forbids unknown keys.
 *     id (UUID): The version 7 identifier of the person.
 *     operator_id (Optional[UUID]): The Operator the person belongs to, ``None`` for a Swarm administrator.
 *     name (str): The full name of the person.
 *     email (str): The email address of the person.
 *     language (Language): The language of the screens the person sees, English by default.
 *     LANGUAGE_FIELD (ClassVar[str]): The name of the ``language`` field.
 *     EMAIL_SEPARATOR (ClassVar[str]): The character that splits an email address into its local part and domain.
 *
 * Notes:
 *     The email check is structural only: one separator, a local part and a domain, and no whitespace.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "Person".
 */
export interface Person {
  email: Email;
  id: Id3;
  language?: Language1;
  name: Name1;
  operator_id?: OperatorId2;
}
/**
 * A role held by a person.
 *
 * Attributes:
 *     model_config (ConfigDict): Forbids unknown keys.
 *     person_id (UUID): The version 7 identifier of the person.
 *     operator_id (Optional[UUID]): The Operator the role applies to, ``None`` for a Swarm administrator.
 *     name (RoleName): The role.
 *
 * Notes:
 *     **``operator_id`` is ``None`` exactly for ``RoleName.SWARM_ADMINISTRATOR``**, because a Swarm administrator
 *     has no access to the data of Operators.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "Role".
 */
export interface Role {
  name: RoleName;
  operator_id?: OperatorId3;
  person_id: PersonId1;
}
/**
 * The frames of every Drone of one Mission at one tick.
 *
 * Attributes:
 *     model_config (ConfigDict): Forbids unknown keys and freezes the squad frame.
 *     mission_id (UUID): The Mission of the frames.
 *     t_us (int): The moment of the tick, in microseconds since the epoch.
 *     frames (List[TelemetryFrame]): One frame per Drone.
 *     T_US_MIN (ClassVar[int]): The smallest accepted ``t_us``.
 *
 * Notes:
 *     - **Every frame must belong to the Mission, and each Drone appears once.**
 *     - The list may be empty.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "SquadFrame".
 */
export interface SquadFrame {
  frames: Frames;
  mission_id: MissionId3;
  t_us: TUs1;
}
/**
 * What one Drone reports at one tick.
 *
 * Attributes:
 *     model_config (ConfigDict): Forbids unknown keys and freezes the frame.
 *     mission_id (UUID): The Mission the frame belongs to.
 *     drone_id (UUID): The Drone that sent the frame.
 *     seq (int): The sequence number per Drone, which detects gaps.
 *     t_us (int): The moment of the frame, in microseconds since the epoch.
 *     lat_e7 (int): The latitude in degrees multiplied by 1e7.
 *     lon_e7 (int): The longitude in degrees multiplied by 1e7.
 *     altitude_m (float): The altitude, in metres.
 *     speed_m_s (float): The speed, in metres per second.
 *     heading_deg (float): The heading, in degrees from north.
 *     battery_pct (float): The battery charge, in percent.
 *     link_quality_pct (float): The quality of the Link, in percent.
 *     state (DroneState): The state of the Drone.
 *     LAT_E7_MIN (ClassVar[int]): The smallest accepted value.
 *     LAT_E7_MAX (ClassVar[int]): The largest accepted value.
 *     LON_E7_MIN (ClassVar[int]): The smallest accepted value.
 *     LON_E7_MAX (ClassVar[int]): The largest accepted value.
 *     SEQ_MIN (ClassVar[int]): The smallest accepted value.
 *     T_US_MIN (ClassVar[int]): The smallest accepted value.
 *     SPEED_M_S_MIN (ClassVar[int]): The smallest accepted value.
 *     HEADING_DEG_MIN (ClassVar[int]): The smallest accepted value.
 *     HEADING_DEG_MAX (ClassVar[int]): The largest accepted value, which is excluded.
 *     BATTERY_PCT_MIN (ClassVar[int]): The smallest accepted value.
 *     BATTERY_PCT_MAX (ClassVar[int]): The largest accepted value.
 *     LINK_QUALITY_PCT_MIN (ClassVar[int]): The smallest accepted value.
 *     LINK_QUALITY_PCT_MAX (ClassVar[int]): The largest accepted value.
 *
 * Notes:
 *     - Latitude and longitude are integers, so that frames stay small.
 *     - **Booleans are refused wherever a number is expected.**
 *     - ``payload_state`` is not part of this version of the frame.
 *
 * This interface was referenced by `SwarmModels`'s JSON-Schema
 * via the `definition` "TelemetryFrame".
 */
export interface TelemetryFrame {
  altitude_m: AltitudeM;
  battery_pct: BatteryPct;
  drone_id: DroneId1;
  heading_deg: HeadingDeg;
  lat_e7: LatE7;
  link_quality_pct: LinkQualityPct;
  lon_e7: LonE7;
  mission_id: MissionId2;
  seq: Seq;
  speed_m_s: SpeedMS;
  state: DroneState1;
  t_us: TUs;
}
