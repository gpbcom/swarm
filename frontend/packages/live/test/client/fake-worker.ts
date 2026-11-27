import type { WorkerLike } from "../../src/client/live-client.ts";
import type { FromWorker, ToWorker } from "../../src/worker/live-worker-messages.ts";

export class FakeWorker implements WorkerLike {
  posted: ToWorker[] = [];
  terminated = 0;
  onmessage: ((event: { data: FromWorker }) => void) | null = null;

  postMessage(message: ToWorker): void {
    this.posted.push(message);
  }

  terminate(): void {
    this.terminated += 1;
  }

  emit(message: FromWorker): void {
    this.onmessage?.({ data: message });
  }
}
