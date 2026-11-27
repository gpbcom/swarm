import type { LatencyHistogram, LiveStatus, SquadSnapshot } from '@swarm/live';

const MICROSECONDS_PER_MILLISECOND = 1000;

/** The part of a LiveClient the feed uses. */
export interface LiveClientLike {
  connect(url: string, missionId: string): void;
  onSnapshot(listener: (snapshot: SquadSnapshot) => void): () => void;
  onStatus(listener: (status: LiveStatus) => void): () => void;
  close(): void;
}

export interface FeedHistograms {
  droneToScreen: LatencyHistogram;
  frameToPixels: LatencyHistogram;
}

/** Bridges the live client to the map's source and records the latency of what is drawn, with no React state per frame. */
export class SquadFeed {
  private readonly client: LiveClientLike;
  private readonly histograms: FeedHistograms;
  private readonly listeners = new Set<() => void>();
  private latest: SquadSnapshot | null = null;
  private unsubscribe: (() => void) | null = null;

  constructor(client: LiveClientLike, histograms: FeedHistograms) {
    this.client = client;
    this.histograms = histograms;
  }

  get count(): number {
    return this.latest?.count ?? 0;
  }

  current(): SquadSnapshot | null {
    return this.latest;
  }

  subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  start(url: string, missionId: string): void {
    this.unsubscribe?.();
    this.unsubscribe = this.client.onSnapshot((snapshot) => {
      this.latest = snapshot;
      for (const listener of Array.from(this.listeners)) listener();
    });
    this.client.connect(url, missionId);
  }

  stop(): void {
    this.unsubscribe?.();
    this.unsubscribe = null;
    this.client.close();
  }

  /** Record the drone to screen latency of each updated slot, and the frame to pixels latency once. */
  drawn(snapshot: SquadSnapshot, drawnAtMs: number): void {
    for (let slot = 0; slot < snapshot.count; slot += 1) {
      if (snapshot.updated[slot] !== 0) {
        const tUs = snapshot.tUs[slot] ?? 0;
        this.histograms.droneToScreen.record(drawnAtMs - tUs / MICROSECONDS_PER_MILLISECOND);
      }
    }
    this.histograms.frameToPixels.record(drawnAtMs - snapshot.receivedAtMs);
  }
}
