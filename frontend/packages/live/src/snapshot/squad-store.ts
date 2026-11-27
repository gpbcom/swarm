import type { SquadFrame } from "../generated/models.ts";
import { DRONE_STATES, type SquadSnapshot } from "./squad-snapshot.ts";

const E7 = 1e-7;

type TypedArray = Float64Array | Float32Array | Uint8Array;

function grow<T extends TypedArray>(array: T, length: number): T {
  const bigger = new (array.constructor as new (length: number) => T)(length);
  bigger.set(array);
  return bigger;
}

/** Merges squad frames into typed arrays, one stable slot per Drone, and hands out transferable snapshots. */
export class SquadStore {
  readonly missionId: string;
  dirty = false;

  private version = 0;
  private receivedAtMs = 0;
  private readonly slots = new Map<string, number>();
  private readonly droneIds: string[] = [];
  private readonly seqs: number[] = [];
  private positions = new Float64Array(0);
  private states = new Uint8Array(0);
  private batteryPct = new Float32Array(0);
  private linkQualityPct = new Float32Array(0);
  private headingDeg = new Float32Array(0);
  private speedMS = new Float32Array(0);
  private tUs = new Float64Array(0);
  private changed = new Uint8Array(0);

  constructor(missionId: string) {
    this.missionId = missionId;
  }

  /** Merge a frame received at `receivedAtMs`; frames of another Mission and stale drone frames are ignored. */
  merge(frame: SquadFrame, receivedAtMs: number): void {
    if (frame.mission_id !== this.missionId) {
      return;
    }
    for (const drone of frame.frames) {
      if (drone.mission_id !== this.missionId) {
        continue;
      }
      let slot = this.slots.get(drone.drone_id);
      if (slot === undefined) {
        slot = this.addSlot(drone.drone_id);
      } else if (drone.seq <= (this.seqs[slot] ?? -Infinity)) {
        continue;
      }
      this.seqs[slot] = drone.seq;
      this.positions[slot * 3] = drone.lon_e7 * E7;
      this.positions[slot * 3 + 1] = drone.lat_e7 * E7;
      this.positions[slot * 3 + 2] = drone.altitude_m;
      this.states[slot] = Math.max(0, DRONE_STATES.indexOf(drone.state));
      this.batteryPct[slot] = drone.battery_pct;
      this.linkQualityPct[slot] = drone.link_quality_pct;
      this.headingDeg[slot] = drone.heading_deg;
      this.speedMS[slot] = drone.speed_m_s;
      this.tUs[slot] = drone.t_us;
      this.changed[slot] = 1;
      this.receivedAtMs = Math.max(this.receivedAtMs, receivedAtMs);
      this.dirty = true;
    }
  }

  /** Copy the squad into fresh buffers, clear the updated marks and the dirty flag. */
  snapshot(): SquadSnapshot {
    const count = this.droneIds.length;
    this.version += 1;
    const snapshot: SquadSnapshot = {
      missionId: this.missionId,
      version: this.version,
      receivedAtMs: this.receivedAtMs,
      count,
      droneIds: [...this.droneIds],
      positions: this.positions.slice(0, count * 3),
      states: this.states.slice(0, count),
      batteryPct: this.batteryPct.slice(0, count),
      linkQualityPct: this.linkQualityPct.slice(0, count),
      headingDeg: this.headingDeg.slice(0, count),
      speedMS: this.speedMS.slice(0, count),
      tUs: this.tUs.slice(0, count),
      updated: this.changed.slice(0, count),
    };
    this.changed.fill(0);
    this.dirty = false;
    return snapshot;
  }

  /** List the distinct array buffers of a snapshot, for `postMessage` to transfer. */
  transferables(snapshot: SquadSnapshot): ArrayBuffer[] {
    const arrays: TypedArray[] = [
      snapshot.positions,
      snapshot.states,
      snapshot.batteryPct,
      snapshot.linkQualityPct,
      snapshot.headingDeg,
      snapshot.speedMS,
      snapshot.tUs,
      snapshot.updated,
    ];
    return [...new Set(arrays.map((array) => array.buffer as ArrayBuffer))];
  }

  private addSlot(droneId: string): number {
    const slot = this.droneIds.length;
    this.slots.set(droneId, slot);
    this.droneIds.push(droneId);
    this.seqs.push(-Infinity);
    if (this.states.length < slot + 1) {
      const capacity = Math.max(8, this.states.length * 2);
      this.positions = grow(this.positions, capacity * 3);
      this.states = grow(this.states, capacity);
      this.batteryPct = grow(this.batteryPct, capacity);
      this.linkQualityPct = grow(this.linkQualityPct, capacity);
      this.headingDeg = grow(this.headingDeg, capacity);
      this.speedMS = grow(this.speedMS, capacity);
      this.tUs = grow(this.tUs, capacity);
      this.changed = grow(this.changed, capacity);
    }
    return slot;
  }
}
