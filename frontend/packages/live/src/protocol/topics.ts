import { encode } from "@msgpack/msgpack";

import type { LiveSubscription } from "../generated/models.ts";
import { LiveTopicInvalidError } from "./live-protocol-errors.ts";

const MISSION_ID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[0-9a-f]{4}-[0-9a-f]{12}$/;

/** Name the squad topic of a Mission, `mission/<id>/squad`. */
export function squadTopic(missionId: string): string {
  if (!MISSION_ID_PATTERN.test(missionId)) {
    throw new LiveTopicInvalidError(missionId);
  }
  return `mission/${missionId}/squad`;
}

/** Encode, as MessagePack, the message that subscribes to the squad topic of a Mission at full rate. */
export function encodeSquadSubscription(missionId: string): Uint8Array {
  const message: LiveSubscription = { op: "subscribe", topic: squadTopic(missionId), rate: "full" };
  return encode(message);
}
