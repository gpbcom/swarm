import { describe, expect, it } from 'vitest';

import { AppConfigError, DEFAULT_APP_CONFIG, loadAppConfig, parseAppConfig } from '../../src/config/app-config';

const MISSION_ID = '01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e01';
const VERSION_4_ID = '550e8400-e29b-41d4-a716-446655440000';

function reply(status: number, body: unknown = {}): (url: string) => Promise<Response> {
  return () => Promise.resolve(new Response(JSON.stringify(body), { status }));
}

describe('ground-control runtime configuration', () => {
  it('gives the defaults for an empty object', () => {
    expect(parseAppConfig({})).toEqual(DEFAULT_APP_CONFIG);
  });

  it('has the documented defaults', () => {
    expect(DEFAULT_APP_CONFIG).toEqual({
      liveUrl: 'ws://127.0.0.1:8080/v1/live',
      missionId: null,
      tilesUrl: 'tiles/basemap.pmtiles',
      metricsUrl: null,
      metricsIntervalS: 60,
      cell: null,
      livePath: 'edge',
    });
  });

  it('takes the keys it is given and the default for the others', () => {
    const config = parseAppConfig({ missionId: MISSION_ID, liveUrl: 'wss://cell.example/v1/live', livePath: 'cell' });
    expect(config.missionId).toBe(MISSION_ID);
    expect(config.liveUrl).toBe('wss://cell.example/v1/live');
    expect(config.livePath).toBe('cell');
    expect(config.tilesUrl).toBe(DEFAULT_APP_CONFIG.tilesUrl);
  });

  it('accepts every key at once', () => {
    const full = {
      liveUrl: 'ws://edge.local/v1/live',
      missionId: MISSION_ID,
      tilesUrl: 'https://tiles.example/basemap.pmtiles',
      metricsUrl: 'https://otel.example/v1/metrics',
      metricsIntervalS: 15,
      cell: 'cell-a',
      livePath: 'cell',
    };
    expect(parseAppConfig(full)).toEqual(full);
  });

  it.each([
    ['an unknown key', { unknown: 1 }],
    ['a http live url', { liveUrl: 'http://127.0.0.1/v1/live' }],
    ['a live url that is not text', { liveUrl: 12 }],
    ['a mission id that is not a UUID', { missionId: 'mission' }],
    ['a mission id of version 4', { missionId: VERSION_4_ID }],
    ['a zero metrics interval', { metricsIntervalS: 0 }],
    ['a negative metrics interval', { metricsIntervalS: -5 }],
    ['a boolean metrics interval', { metricsIntervalS: true }],
    ['a live path outside edge and cell', { livePath: 'satellite' }],
    ['a value that is not an object', 'config'],
  ])('refuses %s', (_name, value) => {
    expect(() => parseAppConfig(value)).toThrow(AppConfigError);
  });

  it('reads the configuration from config.json by default', async () => {
    const asked: string[] = [];
    const config = await loadAppConfig((url) => {
      asked.push(url);
      return Promise.resolve(new Response(JSON.stringify({ cell: 'cell-b' }), { status: 200 }));
    });
    expect(asked).toEqual(['config.json']);
    expect(config.cell).toBe('cell-b');
  });

  it('gives the defaults when the file is not found', async () => {
    expect(await loadAppConfig(reply(404))).toEqual(DEFAULT_APP_CONFIG);
  });

  it('refuses a server error', async () => {
    await expect(loadAppConfig(reply(500))).rejects.toThrow(AppConfigError);
  });

  it('refuses a request that fails', async () => {
    await expect(loadAppConfig(() => Promise.reject(new TypeError('offline')))).rejects.toThrow(AppConfigError);
  });

  it('refuses a file that is not JSON', async () => {
    const notJson = (): Promise<Response> => Promise.resolve(new Response('not json', { status: 200 }));
    await expect(loadAppConfig(notJson)).rejects.toThrow(AppConfigError);
  });

  it('refuses a file with an invalid value', async () => {
    await expect(loadAppConfig(reply(200, { livePath: 'x' }))).rejects.toThrow(AppConfigError);
  });
});
