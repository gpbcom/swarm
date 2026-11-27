import assert from "node:assert/strict";
import { beforeEach, describe, it } from "node:test";

import { LiveClient } from "../../src/client/live-client.ts";
import type { SquadSnapshot } from "../../src/snapshot/squad-snapshot.ts";
import type { LiveStatus } from "../../src/worker/live-worker-messages.ts";
import { FakeWorker } from "./fake-worker.ts";

const MISSION_ID = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e01";
const URL = "ws://gateway.test/v1/live";

function aSnapshot(version: number): SquadSnapshot {
  return {
    version,
    missionId: MISSION_ID,
    count: 1,
    droneIds: ["01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4f01"],
    positions: new Float64Array([20, 1, 30]),
    states: new Uint8Array([2]),
    batteryPct: new Float32Array([80]),
    linkQualityPct: new Float32Array([90]),
    headingDeg: new Float32Array([90]),
    speedMS: new Float32Array([5]),
    tUs: new Float64Array([1_000_000]),
    updated: new Uint8Array([1]),
    receivedAtMs: 10,
  };
}

describe("the live client", () => {
  let worker: FakeWorker;
  let client: LiveClient;
  let created: number;

  beforeEach(() => {
    worker = new FakeWorker();
    created = 0;
    client = new LiveClient(() => {
      created += 1;
      return worker;
    });
  });

  it("posts connect to the worker with the url and the mission", () => {
    client.connect(URL, MISSION_ID);
    assert.equal(created, 1);
    assert.deepEqual(worker.posted, [{ kind: "connect", url: URL, missionId: MISSION_ID }]);
  });

  it("forwards a snapshot of the worker to its listeners as it is", () => {
    const received: SquadSnapshot[] = [];
    client.onSnapshot((snapshot: SquadSnapshot) => received.push(snapshot));
    client.connect(URL, MISSION_ID);
    const snapshot = aSnapshot(1);
    worker.emit({ kind: "snapshot", snapshot });
    assert.equal(received.length, 1);
    assert.equal(received[0], snapshot);
  });

  it("forwards a status of the worker to its listeners", () => {
    const received: LiveStatus[] = [];
    client.onStatus((status: LiveStatus) => received.push(status));
    client.connect(URL, MISSION_ID);
    worker.emit({ kind: "status", status: "connecting" });
    worker.emit({ kind: "status", status: "open" });
    assert.deepEqual(received, ["connecting", "open"]);
  });

  it("keeps snapshots and statuses apart", () => {
    const snapshots: SquadSnapshot[] = [];
    const statuses: LiveStatus[] = [];
    client.onSnapshot((snapshot: SquadSnapshot) => snapshots.push(snapshot));
    client.onStatus((status: LiveStatus) => statuses.push(status));
    client.connect(URL, MISSION_ID);
    worker.emit({ kind: "status", status: "open" });
    assert.equal(snapshots.length, 0);
    assert.equal(statuses.length, 1);
  });

  it("delivers to every listener", () => {
    let first = 0;
    let second = 0;
    client.onSnapshot(() => (first += 1));
    client.onSnapshot(() => (second += 1));
    client.connect(URL, MISSION_ID);
    worker.emit({ kind: "snapshot", snapshot: aSnapshot(1) });
    assert.deepEqual([first, second], [1, 1]);
  });

  it("stops delivering to a snapshot listener once it unsubscribes", () => {
    let count = 0;
    const unsubscribe = client.onSnapshot(() => (count += 1));
    client.connect(URL, MISSION_ID);
    worker.emit({ kind: "snapshot", snapshot: aSnapshot(1) });
    unsubscribe();
    worker.emit({ kind: "snapshot", snapshot: aSnapshot(2) });
    assert.equal(count, 1);
  });

  it("stops delivering to a status listener once it unsubscribes", () => {
    let count = 0;
    const unsubscribe = client.onStatus(() => (count += 1));
    client.connect(URL, MISSION_ID);
    worker.emit({ kind: "status", status: "open" });
    unsubscribe();
    worker.emit({ kind: "status", status: "closed" });
    assert.equal(count, 1);
  });

  it("posts close to the worker and terminates it on close", () => {
    client.connect(URL, MISSION_ID);
    client.close();
    assert.deepEqual(worker.posted.at(-1), { kind: "close" });
    assert.equal(worker.terminated, 1);
  });

  it("only posts connect and close to the worker", () => {
    client.connect(URL, MISSION_ID);
    worker.emit({ kind: "snapshot", snapshot: aSnapshot(1) });
    client.close();
    assert.deepEqual(
      worker.posted.map((message) => message.kind),
      ["connect", "close"],
    );
  });
});
