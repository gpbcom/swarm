import assert from "node:assert/strict";
import { beforeEach, describe, it } from "node:test";

import { decode, encode } from "@msgpack/msgpack";

import { LiveWorkerCore } from "../../src/worker/live-worker-core.ts";
import type { FromWorker, LiveStatus } from "../../src/worker/live-worker-messages.ts";
import type { SquadSnapshot } from "../../src/snapshot/squad-snapshot.ts";
import { FakeClock } from "./fake-clock.ts";
import { FakeSocket } from "./fake-socket.ts";

const MISSION_ID = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e01";
const DRONE_IDS: string[] = ["01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4f01", "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4f02"];
const URL = "ws://gateway.test/v1/live";
const WINDOW_MS = 1000;
const MAX_PER_S = 30;

interface Posted {
  message: FromWorker;
  transfer: ArrayBuffer[];
}

function aFrame(seq: number, tUs: number, lat = 1): ArrayBuffer {
  const frames = DRONE_IDS.map((droneId: string) => ({
    mission_id: MISSION_ID,
    drone_id: droneId,
    seq,
    t_us: tUs,
    lat_e7: Math.round(lat * 1e7),
    lon_e7: 20_000_000,
    altitude_m: 30,
    speed_m_s: 5,
    heading_deg: 90,
    battery_pct: 80,
    link_quality_pct: 90,
    state: "airborne",
  }));
  const bytes: Uint8Array = encode({ mission_id: MISSION_ID, t_us: tUs, frames });
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
}

describe("the live worker core", () => {
  let clock: FakeClock;
  let sockets: FakeSocket[];
  let posted: Posted[];
  let core: LiveWorkerCore;

  const snapshots = (): SquadSnapshot[] =>
    posted.flatMap((entry: Posted) => (entry.message.kind === "snapshot" ? [entry.message.snapshot] : []));
  const statuses = (): LiveStatus[] =>
    posted.flatMap((entry: Posted) => (entry.message.kind === "status" ? [entry.message.status] : []));

  beforeEach(() => {
    clock = new FakeClock();
    sockets = [];
    posted = [];
    core = new LiveWorkerCore(
      (url: string) => {
        const socket = new FakeSocket(url);
        sockets.push(socket);
        return socket;
      },
      (message: FromWorker, transfer: ArrayBuffer[]) => {
        posted.push({ message, transfer });
      },
      clock,
    );
  });

  function connect(): FakeSocket {
    core.handle({ kind: "connect", url: URL, missionId: MISSION_ID });
    const socket = sockets[0];
    assert.ok(socket);
    return socket;
  }

  it("opens one socket for the url with binary type arraybuffer", () => {
    const socket = connect();
    assert.equal(sockets.length, 1);
    assert.equal(socket.url, URL);
    assert.equal(socket.binaryType, "arraybuffer");
  });

  it("posts connecting at once and open when the socket opens", () => {
    const socket = connect();
    assert.deepEqual(statuses(), ["connecting"]);
    socket.fireOpen();
    assert.deepEqual(statuses(), ["connecting", "open"]);
  });

  it("sends exactly one subscription for the squad topic on open", () => {
    const socket = connect();
    assert.equal(socket.sent.length, 0);
    socket.fireOpen();
    assert.equal(socket.sent.length, 1);
    const sent = socket.sent[0];
    assert.ok(sent);
    assert.deepEqual(decode(sent), {
      op: "subscribe",
      topic: `mission/${MISSION_ID}/squad`,
      rate: "full",
    });
  });

  it("posts a snapshot of the decoded frame with its buffers in the transfer list", () => {
    const socket = connect();
    socket.fireOpen();
    socket.fireMessage(aFrame(1, 1_000_000));
    clock.advance(100);
    const list = snapshots();
    assert.equal(list.length, 1);
    const snapshot = list[0];
    assert.ok(snapshot);
    assert.equal(snapshot.missionId, MISSION_ID);
    assert.equal(snapshot.count, DRONE_IDS.length);
    assert.deepEqual([...snapshot.droneIds].sort(), [...DRONE_IDS].sort());
    const entry = posted.find((item: Posted) => item.message.kind === "snapshot");
    assert.ok(entry);
    assert.ok(entry.transfer.includes(snapshot.positions.buffer as ArrayBuffer));
    assert.ok(entry.transfer.includes(snapshot.states.buffer as ArrayBuffer));
    assert.ok(entry.transfer.every((buffer: ArrayBuffer) => buffer instanceof ArrayBuffer));
  });

  it("gives one snapshot for several frames arriving within one interval", () => {
    const socket = connect();
    socket.fireOpen();
    socket.fireMessage(aFrame(1, 1_000_000));
    socket.fireMessage(aFrame(2, 1_010_000));
    socket.fireMessage(aFrame(3, 1_020_000));
    clock.advance(100);
    assert.equal(snapshots().length, 1);
  });

  it("never posts more than thirty snapshots in one second", () => {
    const socket = connect();
    socket.fireOpen();
    for (let step = 0; step < WINDOW_MS / 5; step += 1) {
      socket.fireMessage(aFrame(step + 1, 1_000_000 + step * 5000, 1 + step / 1000));
      clock.advance(5);
    }
    const count = snapshots().length;
    assert.ok(count >= 1);
    assert.ok(count <= MAX_PER_S, `posted ${String(count)} snapshots`);
  });

  it("posts no snapshot when nothing changed", () => {
    const socket = connect();
    socket.fireOpen();
    socket.fireMessage(aFrame(1, 1_000_000));
    clock.advance(WINDOW_MS);
    assert.equal(snapshots().length, 1);
    clock.advance(WINDOW_MS);
    assert.equal(snapshots().length, 1);
  });

  it("posts no snapshot before any frame", () => {
    const socket = connect();
    socket.fireOpen();
    clock.advance(WINDOW_MS);
    assert.equal(snapshots().length, 0);
  });

  it("skips an unreadable message and keeps the socket open", () => {
    const socket = connect();
    socket.fireOpen();
    socket.fireMessage(Uint8Array.of(0xc1).buffer);
    socket.fireMessage(encode({ unexpected: true }).buffer.slice(0));
    clock.advance(WINDOW_MS);
    assert.equal(snapshots().length, 0);
    assert.equal(socket.closeCalls, 0);
    assert.ok(!statuses().includes("closed"));
    assert.ok(!statuses().includes("failed"));
    socket.fireMessage(aFrame(1, 1_000_000));
    clock.advance(100);
    assert.equal(snapshots().length, 1);
  });

  it("closes the socket and posts closed when told to close", () => {
    const socket = connect();
    socket.fireOpen();
    core.handle({ kind: "close" });
    assert.equal(socket.closeCalls, 1);
    assert.equal(statuses().at(-1), "closed");
  });

  it("stops the timer on close", () => {
    const socket = connect();
    socket.fireOpen();
    socket.fireMessage(aFrame(1, 1_000_000));
    core.handle({ kind: "close" });
    clock.advance(WINDOW_MS);
    assert.equal(clock.pending(), 0);
    assert.equal(snapshots().length, 0);
  });

  it("posts closed and stops the timer when the socket closes", () => {
    const socket = connect();
    socket.fireOpen();
    socket.fireMessage(aFrame(1, 1_000_000));
    socket.fireClose();
    assert.equal(statuses().at(-1), "closed");
    clock.advance(WINDOW_MS);
    assert.equal(clock.pending(), 0);
  });

  it("posts failed when the socket errors", () => {
    const socket = connect();
    socket.fireError();
    assert.equal(statuses().at(-1), "failed");
  });

  it("does not reconnect after the socket closes", () => {
    const socket = connect();
    socket.fireOpen();
    socket.fireClose();
    clock.advance(60 * WINDOW_MS);
    assert.equal(sockets.length, 1);
  });

  it("does not reconnect after an error", () => {
    const socket = connect();
    socket.fireError();
    socket.fireClose();
    clock.advance(60 * WINDOW_MS);
    assert.equal(sockets.length, 1);
  });
});
