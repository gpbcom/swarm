import { encode } from "@msgpack/msgpack";

import type { DroneState, SquadFrame, TelemetryFrame } from "../../src/generated/models.ts";

export const MISSION_ID = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e01";
export const OTHER_MISSION_ID = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e02";
export const T_US = 1_790_000_000_000_000;

export function droneId(index: number): string {
  return `01943c5e-8a4b-7c2d-9e1f-0a1b2c3d5${String(index).padStart(3, "0")}`;
}

export function aTelemetryFrame(
  missionId: string,
  index: number,
  overrides: Partial<TelemetryFrame> = {},
): TelemetryFrame {
  const state: DroneState = "airborne";
  return {
    mission_id: missionId,
    drone_id: droneId(index),
    seq: 1,
    t_us: T_US,
    lat_e7: 485_000_000 + index * 1_000,
    lon_e7: 23_000_000 + index * 2_000,
    altitude_m: 40 + index,
    speed_m_s: 5.5,
    heading_deg: 90,
    battery_pct: 80,
    link_quality_pct: 95,
    state,
    ...overrides,
  };
}

export function aSquadFrame(missionId: string, drones: number, tUs: number = T_US): SquadFrame {
  const frames: TelemetryFrame[] = [];
  for (let index = 0; index < drones; index += 1) {
    frames.push(aTelemetryFrame(missionId, index, { t_us: tUs }));
  }
  return { mission_id: missionId, t_us: tUs, frames };
}

export function encodedSquadFrame(frame: SquadFrame): Uint8Array {
  return encode(frame);
}
