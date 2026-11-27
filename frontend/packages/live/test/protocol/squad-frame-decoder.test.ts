import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { encode } from "@msgpack/msgpack";

import { LiveMessageUnreadableError } from "../../src/protocol/live-protocol-errors.ts";
import { decodeSquadFrame } from "../../src/protocol/squad-frame-decoder.ts";
import { MISSION_ID, aSquadFrame, droneId, encodedSquadFrame } from "./frames.ts";

function withFirstFrame(changes: Record<string, unknown>): Uint8Array {
  const frame = aSquadFrame(MISSION_ID, 2);
  return encode({ ...frame, frames: [{ ...frame.frames[0], ...changes }, frame.frames[1]] });
}

function withoutFirstFrameField(field: string): Uint8Array {
  const frame = aSquadFrame(MISSION_ID, 2);
  const first: Record<string, unknown> = Object.fromEntries(
    Object.entries(frame.frames[0] ?? {}).filter(([key]) => key !== field),
  );
  return encode({ ...frame, frames: [first, frame.frames[1]] });
}

describe("the squad frame decoder", () => {
  it("decodes a valid frame of ten drones", () => {
    const frame = aSquadFrame(MISSION_ID, 10);
    const decoded = decodeSquadFrame(encodedSquadFrame(frame));
    assert.deepEqual(decoded, frame);
    assert.equal(decoded.frames.length, 10);
    assert.equal(decoded.frames[3]?.drone_id, droneId(3));
  });

  it("decodes a frame given as an array buffer", () => {
    const frame = aSquadFrame(MISSION_ID, 3);
    const bytes = encodedSquadFrame(frame);
    const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
    assert.deepEqual(decodeSquadFrame(buffer), frame);
  });

  it("decodes a frame without drones", () => {
    assert.equal(decodeSquadFrame(encodedSquadFrame(aSquadFrame(MISSION_ID, 0))).frames.length, 0);
  });

  it("refuses bytes that are not message pack", () => {
    assert.throws(() => decodeSquadFrame(new Uint8Array([0xc1, 0xc1, 0xc1])), LiveMessageUnreadableError);
  });

  it("refuses a message pack value that is not a map", () => {
    assert.throws(() => decodeSquadFrame(encode([1, 2, 3])), LiveMessageUnreadableError);
  });

  it("refuses a frame without its mission id", () => {
    const rest: Record<string, unknown> = Object.fromEntries(
      Object.entries(aSquadFrame(MISSION_ID, 1)).filter(([key]) => key !== "mission_id"),
    );
    assert.throws(() => decodeSquadFrame(encode(rest)), LiveMessageUnreadableError);
  });

  it("refuses a drone frame with a missing field", () => {
    assert.throws(() => decodeSquadFrame(withoutFirstFrameField("battery_pct")), LiveMessageUnreadableError);
  });

  it("refuses a drone frame with a mistyped field", () => {
    assert.throws(() => decodeSquadFrame(withFirstFrame({ altitude_m: "high" })), LiveMessageUnreadableError);
  });

  it("refuses a state outside the drone states", () => {
    assert.throws(() => decodeSquadFrame(withFirstFrame({ state: "flying" })), LiveMessageUnreadableError);
  });

  it("refuses a boolean where a number is expected", () => {
    assert.throws(() => decodeSquadFrame(withFirstFrame({ seq: true })), LiveMessageUnreadableError);
  });
});
