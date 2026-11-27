import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { decode } from "@msgpack/msgpack";

import { LiveTopicInvalidError } from "../../src/protocol/live-protocol-errors.ts";
import { encodeSquadSubscription, squadTopic } from "../../src/protocol/topics.ts";
import { MISSION_ID } from "./frames.ts";

describe("the squad topic and subscription", () => {
  it("names the squad topic of a mission", () => {
    assert.equal(squadTopic(MISSION_ID), `mission/${MISSION_ID}/squad`);
  });

  it("encodes a subscribe message that decodes to the expected map", () => {
    const message: unknown = decode(encodeSquadSubscription(MISSION_ID));
    assert.deepEqual(message, { op: "subscribe", topic: `mission/${MISSION_ID}/squad`, rate: "full" });
  });

  it("returns the subscription as bytes", () => {
    assert.ok(encodeSquadSubscription(MISSION_ID) instanceof Uint8Array);
  });

  for (const bad of ["", "not-a-uuid", "01943c5e-8a4b-4c2d-9e1f-0a1b2c3d4e01", "mission/../squad"]) {
    it(`refuses the topic of the mission id ${JSON.stringify(bad)}`, () => {
      assert.throws(() => squadTopic(bad), LiveTopicInvalidError);
    });

    it(`refuses to subscribe to the mission id ${JSON.stringify(bad)}`, () => {
      assert.throws(() => encodeSquadSubscription(bad), LiveTopicInvalidError);
    });
  }
});
