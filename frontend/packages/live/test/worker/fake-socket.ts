import type { SocketLike } from "../../src/worker/live-worker-core.ts";

export class FakeSocket implements SocketLike {
  binaryType = "blob";
  sent: Uint8Array[] = [];
  closeCalls = 0;
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: ArrayBuffer }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;

  readonly url: string;

  constructor(url: string) {
    this.url = url;
  }

  send(data: Uint8Array): void {
    this.sent.push(data);
  }

  close(): void {
    this.closeCalls += 1;
  }

  fireOpen(): void {
    this.onopen?.();
  }

  fireMessage(data: ArrayBuffer): void {
    this.onmessage?.({ data });
  }

  fireClose(): void {
    this.onclose?.();
  }

  fireError(): void {
    this.onerror?.();
  }
}
