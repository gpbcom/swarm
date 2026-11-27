import type { SquadSnapshot } from "../snapshot/squad-snapshot.ts";

/** The state of the worker's socket, as the main thread sees it. */
export type LiveStatus = "connecting" | "open" | "closed" | "failed";

/** The messages the main thread posts to the live worker. */
export type ToWorker = { kind: "connect"; url: string; missionId: string; endpoint?: string; cell?: string } | { kind: "close" };

/** The messages the live worker posts to the main thread. */
export type FromWorker = { kind: "snapshot"; snapshot: SquadSnapshot } | { kind: "status"; status: LiveStatus };
