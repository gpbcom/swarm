import type { DroneState } from "../generated/models.ts";

/** The drone states in the order of their codes in `SquadSnapshot.states`. */
export const DRONE_STATES: readonly DroneState[] = ["ready", "grounded", "airborne", "returning", "landed", "lost"];

/** The squad as typed arrays, one slot per Drone, ready to be transferred to the main thread. */
export interface SquadSnapshot {
  missionId: string;
  version: number;
  receivedAtMs: number;
  count: number;
  droneIds: string[];
  /** Longitude, latitude (degrees) and altitude (metres) of each slot, three values per slot. */
  positions: Float64Array;
  states: Uint8Array;
  batteryPct: Float32Array;
  linkQualityPct: Float32Array;
  headingDeg: Float32Array;
  speedMS: Float32Array;
  tUs: Float64Array;
  /** 1 for a slot changed since the previous snapshot. */
  updated: Uint8Array;
}
