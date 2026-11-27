import { encodeSquadSubscription } from "../protocol/topics.ts";
import { decodeSquadFrame } from "../protocol/squad-frame-decoder.ts";
import { SquadStore } from "../snapshot/squad-store.ts";
import type { FromWorker, LiveStatus, ToWorker } from "./live-worker-messages.ts";

const MS_PER_S = 1000;

/** The part of a WebSocket the worker uses. */
export interface SocketLike {
  binaryType: string;
  onopen: (() => void) | null;
  onmessage: ((event: { data: ArrayBuffer }) => void) | null;
  onclose: (() => void) | null;
  onerror: (() => void) | null;
  send(data: Uint8Array): void;
  close(): void;
}

/** Time and timers, replaceable in tests. */
export interface WorkerClock {
  nowMs(): number;
  setTimer(callback: () => void, delayMs: number): number;
  clearTimer(id: number): void;
}

export type SocketFactory = (url: string) => SocketLike;
export type PostFunction = (message: FromWorker, transfer: ArrayBuffer[]) => void;

/** Owns the socket, decodes and merges frames, and posts at most `maxSnapshotsPerS` snapshots a second. */
export class LiveWorkerCore {
  private readonly openSocket: SocketFactory;
  private readonly post: PostFunction;
  private readonly clock: WorkerClock;
  private readonly intervalMs: number;
  private socket: SocketLike | null = null;
  private store: SquadStore | null = null;
  private timer: number | null = null;

  constructor(openSocket: SocketFactory, post: PostFunction, clock: WorkerClock, maxSnapshotsPerS = 30) {
    this.openSocket = openSocket;
    this.post = post;
    this.clock = clock;
    this.intervalMs = Math.ceil(MS_PER_S / maxSnapshotsPerS);
  }

  /** Handle a message of the main thread. */
  handle(message: ToWorker): void {
    if (message.kind === "connect") {
      this.connect(message.url, message.missionId);
    } else {
      this.close();
    }
  }

  private connect(url: string, missionId: string): void {
    this.store = new SquadStore(missionId);
    const socket = this.openSocket(url);
    this.socket = socket;
    socket.binaryType = "arraybuffer";
    this.status("connecting");
    socket.onopen = () => {
      socket.send(encodeSquadSubscription(missionId));
      this.status("open");
    };
    socket.onmessage = (event) => {
      this.receive(event.data);
    };
    socket.onclose = () => {
      this.stopTimer();
      this.status("closed");
    };
    socket.onerror = () => {
      this.stopTimer();
      this.status("failed");
    };
  }

  private close(): void {
    this.stopTimer();
    const socket = this.socket;
    this.socket = null;
    if (socket) {
      socket.onopen = null;
      socket.onmessage = null;
      socket.onclose = null;
      socket.onerror = null;
      socket.close();
    }
    this.status("closed");
  }

  private receive(data: ArrayBuffer): void {
    const store = this.store;
    if (!store) return;
    try {
      store.merge(decodeSquadFrame(data), this.clock.nowMs());
    } catch {
      return;
    }
    if (store.dirty && this.timer === null) {
      this.timer = this.clock.setTimer(() => {
        this.flush();
      }, this.intervalMs);
    }
  }

  private flush(): void {
    this.timer = null;
    const store = this.store;
    if (!store?.dirty) return;
    const snapshot = store.snapshot();
    this.post({ kind: "snapshot", snapshot }, store.transferables(snapshot));
  }

  private stopTimer(): void {
    if (this.timer !== null) {
      this.clock.clearTimer(this.timer);
      this.timer = null;
    }
  }

  private status(status: LiveStatus): void {
    this.post({ kind: "status", status }, []);
  }
}
