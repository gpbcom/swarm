import { LiveWorkerCore, type SocketLike } from "./live-worker-core.ts";
import type { FromWorker, ToWorker } from "./live-worker-messages.ts";

const scope = self as unknown as {
  postMessage(message: FromWorker, transfer: ArrayBuffer[]): void;
  onmessage: ((event: { data: ToWorker }) => void) | null;
};

const core = new LiveWorkerCore(
  (url: string) => new WebSocket(url) as unknown as SocketLike,
  (message: FromWorker, transfer: ArrayBuffer[]) => {
    scope.postMessage(message, transfer);
  },
  {
    nowMs: () => Date.now(),
    setTimer: (callback: () => void, delayMs: number) => setTimeout(callback, delayMs) as unknown as number,
    clearTimer: (id: number) => {
      clearTimeout(id);
    },
  },
);

scope.onmessage = (event) => {
  core.handle(event.data);
};
