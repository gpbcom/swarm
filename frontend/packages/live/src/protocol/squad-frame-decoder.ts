import { decode } from "@msgpack/msgpack";

import type { SquadFrame, TelemetryFrame } from "../generated/models.ts";
import { DRONE_STATES } from "../snapshot/squad-snapshot.ts";
import { LiveMessageUnreadableError } from "./live-protocol-errors.ts";

type Fields = Record<string, unknown>;

function asMap(value: unknown, what: string): Fields {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new LiveMessageUnreadableError(`${what} is not a map`);
  }
  return value as Fields;
}

function text(fields: Fields, key: string): string {
  const value = fields[key];
  if (typeof value !== "string" || value === "") {
    throw new LiveMessageUnreadableError(`${key} is not a text`);
  }
  return value;
}

function num(fields: Fields, key: string): number {
  const value = fields[key];
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new LiveMessageUnreadableError(`${key} is not a number`);
  }
  return value;
}

function whole(fields: Fields, key: string): number {
  const value = num(fields, key);
  if (!Number.isInteger(value)) {
    throw new LiveMessageUnreadableError(`${key} is not an integer`);
  }
  return value;
}

function telemetry(value: unknown): TelemetryFrame {
  const fields = asMap(value, "a drone frame");
  const state = fields["state"];
  if (typeof state !== "string" || !(DRONE_STATES as readonly string[]).includes(state)) {
    throw new LiveMessageUnreadableError("state is not a drone state");
  }
  return {
    mission_id: text(fields, "mission_id"),
    drone_id: text(fields, "drone_id"),
    seq: whole(fields, "seq"),
    t_us: whole(fields, "t_us"),
    lat_e7: whole(fields, "lat_e7"),
    lon_e7: whole(fields, "lon_e7"),
    altitude_m: num(fields, "altitude_m"),
    speed_m_s: num(fields, "speed_m_s"),
    heading_deg: num(fields, "heading_deg"),
    battery_pct: num(fields, "battery_pct"),
    link_quality_pct: num(fields, "link_quality_pct"),
    state: state as TelemetryFrame["state"],
  };
}

/** Decode and validate one MessagePack squad frame, given as bytes or an array buffer. */
export function decodeSquadFrame(bytes: Uint8Array | ArrayBuffer): SquadFrame {
  let value: unknown;
  try {
    value = decode(bytes);
  } catch (error) {
    throw new LiveMessageUnreadableError("not MessagePack", { cause: error });
  }
  const fields = asMap(value, "the frame");
  const frames = fields["frames"];
  if (!Array.isArray(frames)) {
    throw new LiveMessageUnreadableError("frames is not a list");
  }
  const frame: SquadFrame = {
    mission_id: text(fields, "mission_id"),
    t_us: whole(fields, "t_us"),
    frames: frames.map(telemetry),
  };
  const traceParent = fields["trace_parent"];
  if (typeof traceParent === "string") {
    frame.trace_parent = traceParent;
  } else if (traceParent !== undefined && traceParent !== null) {
    throw new LiveMessageUnreadableError("trace_parent is not a text");
  }
  return frame;
}
