import { act, cleanup, render as renderBare, screen, waitFor } from '@testing-library/react';
import type { RenderResult } from '@testing-library/react';
import type { ReactElement } from 'react';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { I18nProvider } from '@swarm/i18n';

import { DEFAULT_APP_CONFIG } from '../../src/config/app-config';
import type { AppConfig } from '../../src/config/app-config';
import { FlightView } from '../../src/flight/FlightView';
import { FakeLiveClient, FakeSquadMapModule, MAP_LABEL, MISSION_ID, aSnapshot } from './fakes';

interface AView {
  client: FakeLiveClient;
  maps: FakeSquadMapModule;
  result: RenderResult;
}

function render(ui: ReactElement): RenderResult {
  return renderBare(<I18nProvider language="en">{ui}</I18nProvider>);
}

function aView(config: Partial<AppConfig>): AView {
  const client = new FakeLiveClient();
  const maps = new FakeSquadMapModule();
  const result = render(
    <FlightView config={{ ...DEFAULT_APP_CONFIG, ...config }} createLiveClient={() => client} loadMap={maps.loadMap} />,
  );
  return { client, maps, result };
}

interface MetricsBody {
  resourceMetrics: {
    scopeMetrics: { metrics: { name: string; histogram: { dataPoints: { count: number | string }[] } }[] }[];
  }[];
}

describe('flight view', () => {
  const realFetch = globalThis.fetch;
  let posted: string[] = [];

  beforeEach(() => {
    posted = [];
    globalThis.fetch = (_url: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      posted.push(typeof init?.body === 'string' ? init.body : '');
      return Promise.resolve(new Response('{}', { status: 200 }));
    };
  });

  afterEach(() => {
    cleanup();
    globalThis.fetch = realFetch;
  });

  it('loads the map module on demand and shows the labelled region', async () => {
    const { maps } = aView({});
    expect(await screen.findByRole('region', { name: MAP_LABEL })).not.toBeNull();
    expect(maps.loads).toBe(1);
  });

  it('wraps the map in a flight map section that counts no Drone yet', async () => {
    const { result } = aView({});
    await screen.findByRole('region', { name: MAP_LABEL });
    const section = result.container.querySelector('section.flight-map');
    expect(section).not.toBeNull();
    expect(section?.getAttribute('data-drone-count')).toBe('0');
  });

  it('connects the live client with the Mission of the configuration', async () => {
    const { client } = aView({ missionId: MISSION_ID, liveUrl: 'ws://edge.local/v1/live' });
    await screen.findByRole('region', { name: MAP_LABEL });
    expect(client.connects).toEqual([{ url: 'ws://edge.local/v1/live', missionId: MISSION_ID }]);
  });

  it('connects nothing without a Mission and still shows the empty map', async () => {
    const { client } = aView({ missionId: null });
    await screen.findByRole('region', { name: MAP_LABEL });
    expect(client.connects).toEqual([]);
  });

  it('gives the map the tiles url and a source that follows the live client', async () => {
    const { client, maps } = aView({ missionId: MISSION_ID, tilesUrl: 'https://tiles.example/b.pmtiles' });
    await screen.findByRole('region', { name: MAP_LABEL });
    expect(maps.lastProps?.tilesUrl).toBe('https://tiles.example/b.pmtiles');
    const snapshot = aSnapshot(10);
    act(() => {
      client.pushSnapshot(snapshot);
    });
    expect(maps.lastProps?.source.current()).toBe(snapshot);
  });

  it('shows the number of Drones of the latest snapshot', async () => {
    const { client, result } = aView({ missionId: MISSION_ID });
    await screen.findByRole('region', { name: MAP_LABEL });
    act(() => {
      client.pushSnapshot(aSnapshot(10));
    });
    await waitFor(() => {
      expect(result.container.querySelector('section.flight-map')?.getAttribute('data-drone-count')).toBe('10');
    });
  });

  it('records one drone to screen sample per Drone drawn and reports it', async () => {
    const { client, maps } = aView({
      missionId: MISSION_ID,
      metricsUrl: 'https://otel.example/v1/metrics',
      metricsIntervalS: 1,
    });
    await screen.findByRole('region', { name: MAP_LABEL });
    const snapshot = aSnapshot(10, 1_000_000, 1020);
    act(() => {
      client.pushSnapshot(snapshot);
    });
    act(() => {
      maps.drawn(snapshot, 1050);
    });
    await waitFor(() => { expect(posted.length).toBeGreaterThan(0); }, { timeout: 3000 });
    const body = posted.join('');
    expect(body).toContain('swarm.telemetry.drone_to_screen');
    expect(body).toContain('swarm.live.frame_to_pixels');
    expect(body).not.toContain('drone_id');
    const parsed = JSON.parse(posted[0] ?? '{}') as MetricsBody;
    const metrics = parsed.resourceMetrics[0]?.scopeMetrics[0]?.metrics ?? [];
    const droneToScreen = metrics.find((metric) => metric.name === 'swarm.telemetry.drone_to_screen');
    expect(Number(droneToScreen?.histogram.dataPoints[0]?.count)).toBe(10);
  }, 6000);

  it('reports nothing when no metrics url is set', async () => {
    const { client, maps } = aView({ missionId: MISSION_ID, metricsUrl: null, metricsIntervalS: 1 });
    await screen.findByRole('region', { name: MAP_LABEL });
    const snapshot = aSnapshot(2);
    act(() => {
      client.pushSnapshot(snapshot);
    });
    act(() => {
      maps.drawn(snapshot, 1050);
    });
    await new Promise((done) => setTimeout(done, 1300));
    expect(posted).toEqual([]);
  });

  it('closes the live client when it unmounts', async () => {
    const { client, result } = aView({ missionId: MISSION_ID });
    await screen.findByRole('region', { name: MAP_LABEL });
    result.unmount();
    expect(client.closes).toBeGreaterThanOrEqual(1);
  });
});
