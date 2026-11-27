/** Raised when a Mission id cannot name a live topic. */
export class LiveTopicInvalidError extends Error {
  constructor(missionId: string) {
    super(`Invalid Mission id for a live topic: ${JSON.stringify(missionId)}. Must be a version 7 UUID.`);
    this.name = "LiveTopicInvalidError";
  }
}

/** Raised when bytes received on the live socket are not a valid squad frame. */
export class LiveMessageUnreadableError extends Error {
  constructor(reason: string, options?: { cause?: unknown }) {
    super(`Unreadable live message: ${reason}.`, options);
    this.name = "LiveMessageUnreadableError";
  }
}
