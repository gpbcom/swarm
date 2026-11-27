import type { SquadSnapshot } from "../snapshot/squad-snapshot.ts";
import type { FromWorker, LiveStatus, ToWorker } from "../worker/live-worker-messages.ts";

/** The part of a Worker the client uses. */
export interface WorkerLike {
  onmessage: ((event: { data: FromWorker }) => void) | null;
  postMessage(message: ToWorker): void;
  terminate(): void;
}

export type WorkerFactory = () => WorkerLike;

function defaultWorker(): WorkerLike {
  return new Worker(new URL("../worker/live.worker.ts", import.meta.url), { type: "module" }) as unknown as WorkerLike;
}

/** The main thread's handle on the live worker: it forwards connect and close, and hands out what the worker posts. */
export class LiveClient {
  private readonly createWorker: WorkerFactory;
  private readonly snapshotListeners = new Set<(snapshot: SquadSnapshot) => void>();
  private readonly statusListeners = new Set<(status: LiveStatus) => void>();
  private worker: WorkerLike | null = null;

  constructor(createWorker: WorkerFactory = defaultWorker) {
    this.createWorker = createWorker;
  }

  /** Start the worker and ask it to connect to `url` and follow the squad of `missionId`. */
  connect(url: string, missionId: string): void {
    const worker = this.createWorker();
    this.worker = worker;
    worker.onmessage = (event) => {
      const message = event.data;
      if (message.kind === "snapshot") {
        for (const listener of this.snapshotListeners) listener(message.snapshot);
      } else {
        for (const listener of this.statusListeners) listener(message.status);
      }
    };
    worker.postMessage({ kind: "connect", url, missionId });
  }

  /** Listen to snapshots; the result removes the listener. */
  onSnapshot(listener: (snapshot: SquadSnapshot) => void): () => void {
    this.snapshotListeners.add(listener);
    return () => {
      this.snapshotListeners.delete(listener);
    };
  }

  /** Listen to statuses; the result removes the listener. */
  onStatus(listener: (status: LiveStatus) => void): () => void {
    this.statusListeners.add(listener);
    return () => {
      this.statusListeners.delete(listener);
    };
  }

  /** Ask the worker to close its socket, then terminate it. */
  close(): void {
    const worker = this.worker;
    this.worker = null;
    if (worker) {
      worker.postMessage({ kind: "close" });
      worker.terminate();
    }
  }
}
