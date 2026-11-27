import assert from "node:assert/strict";
import { beforeEach, describe, it } from "node:test";

import { DRONE_STATES } from "../../src/snapshot/squad-snapshot.ts";
import { SquadStore } from "../../src/snapshot/squad-store.ts";
import { MISSION_ID, OTHER_MISSION_ID, T_US, aSquadFrame, aTelemetryFrame, droneId } from "../protocol/frames.ts";

describe("the squad store", () => {
  let store: SquadStore;

  beforeEach(() => {
    store = new SquadStore(MISSION_ID);
  });

  it("starts clean with no drone", () => {
    assert.equal(store.dirty, false);
    assert.equal(store.snapshot().count, 0);
  });

  it("lists the drone states in the order of their codes", () => {
    assert.deepEqual([...DRONE_STATES], ["ready", "grounded", "airborne", "returning", "landed", "lost"]);
  });

  it("places each drone in a slot in order of first appearance", () => {
    store.merge(aSquadFrame(MISSION_ID, 3), 1000);
    const snapshot = store.snapshot();
    assert.equal(snapshot.count, 3);
    assert.deepEqual([...snapshot.droneIds], [droneId(0), droneId(1), droneId(2)]);
    assert.equal(snapshot.missionId, MISSION_ID);
  });

  it("keeps the slot of a drone when a later frame lists drones in another order", () => {
    store.merge(aSquadFrame(MISSION_ID, 2), 1000);
    store.merge(
      {
        mission_id: MISSION_ID,
        t_us: T_US + 1,
        frames: [aTelemetryFrame(MISSION_ID, 1, { seq: 2 }), aTelemetryFrame(MISSION_ID, 2, { seq: 1 })],
      },
      1100,
    );
    assert.deepEqual([...store.snapshot().droneIds], [droneId(0), droneId(1), droneId(2)]);
  });

  it("converts the coordinates by 1e-7 into longitude, latitude and altitude", () => {
    store.merge(
      {
        mission_id: MISSION_ID,
        t_us: T_US,
        frames: [aTelemetryFrame(MISSION_ID, 0, { lat_e7: 485_000_000, lon_e7: 23_000_000, altitude_m: 42.5 })],
      },
      1000,
    );
    const { positions } = store.snapshot();
    assert.ok(Math.abs((positions[0] ?? 0) - 2.3) < 1e-9);
    assert.ok(Math.abs((positions[1] ?? 0) - 48.5) < 1e-9);
    assert.equal(positions[2], 42.5);
  });

  it("stores state codes, battery, link, heading, speed and time", () => {
    store.merge(
      {
        mission_id: MISSION_ID,
        t_us: T_US,
        frames: [
          aTelemetryFrame(MISSION_ID, 0, {
            state: "returning",
            battery_pct: 55,
            link_quality_pct: 70,
            heading_deg: 180,
            speed_m_s: 7,
          }),
        ],
      },
      1000,
    );
    const snapshot = store.snapshot();
    assert.equal(snapshot.states[0], DRONE_STATES.indexOf("returning"));
    assert.equal(snapshot.batteryPct[0], 55);
    assert.equal(snapshot.linkQualityPct[0], 70);
    assert.equal(snapshot.headingDeg[0], 180);
    assert.equal(snapshot.speedMS[0], 7);
    assert.equal(snapshot.tUs[0], T_US);
  });

  it("ignores a frame of another mission", () => {
    store.merge(aSquadFrame(OTHER_MISSION_ID, 2), 1000);
    assert.equal(store.dirty, false);
    assert.equal(store.snapshot().count, 0);
  });

  it("ignores a drone frame whose sequence is not greater than the last seen", () => {
    store.merge(
      { mission_id: MISSION_ID, t_us: T_US, frames: [aTelemetryFrame(MISSION_ID, 0, { seq: 5, battery_pct: 60 })] },
      1000,
    );
    store.snapshot();
    for (const seq of [5, 4]) {
      store.merge(
        { mission_id: MISSION_ID, t_us: T_US, frames: [aTelemetryFrame(MISSION_ID, 0, { seq, battery_pct: 10 })] },
        1100,
      );
    }
    assert.equal(store.dirty, false);
    assert.equal(store.snapshot().batteryPct[0], 60);
  });

  it("keeps the last values of a drone absent from a frame", () => {
    store.merge(aSquadFrame(MISSION_ID, 2), 1000);
    store.snapshot();
    store.merge(
      { mission_id: MISSION_ID, t_us: T_US + 1, frames: [aTelemetryFrame(MISSION_ID, 1, { seq: 2, battery_pct: 30 })] },
      1100,
    );
    const snapshot = store.snapshot();
    assert.equal(snapshot.batteryPct[0], 80);
    assert.equal(snapshot.batteryPct[1], 30);
    assert.equal(snapshot.count, 2);
  });

  it("returns fresh buffers so that later merges do not change a snapshot already taken", () => {
    store.merge(aSquadFrame(MISSION_ID, 1), 1000);
    const first = store.snapshot();
    store.merge(
      { mission_id: MISSION_ID, t_us: T_US + 1, frames: [aTelemetryFrame(MISSION_ID, 0, { seq: 2, battery_pct: 1 })] },
      1100,
    );
    const second = store.snapshot();
    assert.equal(first.batteryPct[0], 80);
    assert.equal(second.batteryPct[0], 1);
    assert.notEqual(first.batteryPct.buffer, second.batteryPct.buffer);
  });

  it("increments the version at each snapshot", () => {
    store.merge(aSquadFrame(MISSION_ID, 1), 1000);
    const first = store.snapshot();
    const second = store.snapshot();
    assert.equal(second.version, first.version + 1);
  });

  it("marks as updated only the slots changed since the previous snapshot", () => {
    store.merge(aSquadFrame(MISSION_ID, 3), 1000);
    assert.deepEqual([...store.snapshot().updated], [1, 1, 1]);
    store.merge(
      { mission_id: MISSION_ID, t_us: T_US + 1, frames: [aTelemetryFrame(MISSION_ID, 1, { seq: 2 })] },
      1100,
    );
    assert.deepEqual([...store.snapshot().updated], [0, 1, 0]);
  });

  it("carries the newest reception time", () => {
    store.merge(aSquadFrame(MISSION_ID, 1), 1000);
    store.merge(
      { mission_id: MISSION_ID, t_us: T_US + 1, frames: [aTelemetryFrame(MISSION_ID, 0, { seq: 2 })] },
      1500,
    );
    assert.equal(store.snapshot().receivedAtMs, 1500);
  });

  it("is dirty after a merge and clean after a snapshot", () => {
    store.merge(aSquadFrame(MISSION_ID, 1), 1000);
    assert.equal(store.dirty, true);
    store.snapshot();
    assert.equal(store.dirty, false);
  });

  it("lists the distinct array buffers of a snapshot as transferables", () => {
    store.merge(aSquadFrame(MISSION_ID, 2), 1000);
    const snapshot = store.snapshot();
    const buffers = store.transferables(snapshot);
    assert.ok(buffers.length > 0);
    assert.equal(new Set(buffers).size, buffers.length);
    assert.ok(buffers.includes(snapshot.positions.buffer as ArrayBuffer));
    assert.ok(buffers.includes(snapshot.states.buffer as ArrayBuffer));
  });
});
