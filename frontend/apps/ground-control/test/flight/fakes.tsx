import type { ComponentType, ReactElement } from 'react';

import type { SquadSnapshot } from '@swarm/live';

export const MISSION_ID = '01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e01';
export const MAP_LABEL = 'Map of the Squad';

export type StatusName = 'connecting' | 'open' | 'closed' | 'failed';

export interface FakeSource {
  current(): SquadSnapshot | null;
  subscribe(listener: () => void): () => void;
}

export interface FakeMapProps {
  tilesUrl: string;
  label: string;
  source: FakeSource;
  onDrawn?: (data: SquadSnapshot, drawnAtMs: number) => void;
}

export interface FakeMapModule {
  SquadMap: ComponentType<FakeMapProps>;
}

export function aSnapshot(count: number, tUs = 1_000_000, receivedAtMs = 1000, version = 1): SquadSnapshot {
  return {
    version,
    missionId: MISSION_ID,
    count,
    droneIds: Array.from({ length: count }, (_, slot) => `drone-${String(slot)}`),
    positions: new Float64Array(count * 3),
    states: new Uint8Array(count),
    batteryPct: new Float32Array(count),
    linkQualityPct: new Float32Array(count),
    headingDeg: new Float32Array(count),
    speedMS: new Float32Array(count),
    tUs: new Float64Array(count).fill(tUs),
    updated: new Uint8Array(count).fill(1),
    receivedAtMs,
  };
}

export class FakeLiveClient {
  connects: { url: string; missionId: string }[] = [];
  closes = 0;
  private snapshotListeners = new Set<(snapshot: SquadSnapshot) => void>();
  private statusListeners = new Set<(status: StatusName) => void>();

  connect(url: string, missionId: string): void {
    this.connects.push({ url, missionId });
  }

  onSnapshot(listener: (snapshot: SquadSnapshot) => void): () => void {
    this.snapshotListeners.add(listener);
    return () => {
      this.snapshotListeners.delete(listener);
    };
  }

  onStatus(listener: (status: StatusName) => void): () => void {
    this.statusListeners.add(listener);
    return () => {
      this.statusListeners.delete(listener);
    };
  }

  close(): void {
    this.closes += 1;
  }

  pushSnapshot(snapshot: SquadSnapshot): void {
    for (const listener of Array.from(this.snapshotListeners)) listener(snapshot);
  }

  pushStatus(status: StatusName): void {
    for (const listener of Array.from(this.statusListeners)) listener(status);
  }
}

export class FakeSquadMapModule {
  loads = 0;
  lastProps: FakeMapProps | null = null;

  readonly loadMap = (): Promise<FakeMapModule> => {
    this.loads += 1;
    const record = (props: FakeMapProps): void => {
      this.lastProps = props;
    };
    const SquadMap = (props: FakeMapProps): ReactElement => {
      record(props);
      return <div className="map" role="region" aria-label={props.label} />;
    };
    return Promise.resolve({ SquadMap });
  };

  drawn(snapshot: SquadSnapshot, drawnAtMs: number): void {
    this.lastProps?.onDrawn?.(snapshot, drawnAtMs);
  }
}
