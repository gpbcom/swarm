export type LivePath = 'edge' | 'cell';

export interface AppConfig {
  liveUrl: string;
  missionId: string | null;
  tilesUrl: string;
  metricsUrl: string | null;
  metricsIntervalS: number;
  cell: string | null;
  livePath: LivePath;
}

export const DEFAULT_APP_CONFIG: AppConfig = {
  liveUrl: 'ws://127.0.0.1:8080/v1/live',
  missionId: null,
  tilesUrl: 'tiles/basemap.pmtiles',
  metricsUrl: null,
  metricsIntervalS: 60,
  cell: null,
  livePath: 'edge',
};

export class AppConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AppConfigError';
  }
}

const UUID_V7 = /^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const KEYS = Object.keys(DEFAULT_APP_CONFIG);

function text(key: string, value: unknown): string {
  if (typeof value !== 'string' || value.trim() === '') {
    throw new AppConfigError(`Invalid ${key}: expected a non-empty text.`);
  }
  return value;
}

function nullableText(key: string, value: unknown): string | null {
  return value === null ? null : text(key, value);
}

function checked(key: string, value: unknown): AppConfig[keyof AppConfig] {
  switch (key) {
    case 'liveUrl': {
      const url = text(key, value);
      if (!/^wss?:\/\//.test(url)) {
        throw new AppConfigError('Invalid liveUrl: expected a ws:// or wss:// URL.');
      }
      return url;
    }
    case 'missionId': {
      const id = nullableText(key, value);
      if (id !== null && !UUID_V7.test(id)) {
        throw new AppConfigError('Invalid missionId: expected a UUID version 7.');
      }
      return id;
    }
    case 'tilesUrl':
      return text(key, value);
    case 'metricsUrl':
    case 'cell':
      return nullableText(key, value);
    case 'metricsIntervalS':
      if (typeof value !== 'number' || !Number.isFinite(value) || value <= 0) {
        throw new AppConfigError('Invalid metricsIntervalS: expected a positive number.');
      }
      return value;
    default:
      if (value !== 'edge' && value !== 'cell') {
        throw new AppConfigError('Invalid livePath: expected edge or cell.');
      }
      return value;
  }
}

export function parseAppConfig(value: unknown): AppConfig {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new AppConfigError('Invalid configuration: expected an object.');
  }
  const given = value as Record<string, unknown>;
  for (const key of Object.keys(given)) {
    if (!KEYS.includes(key)) {
      throw new AppConfigError(`Unknown configuration key: ${key}.`);
    }
  }
  const result: Record<string, unknown> = { ...DEFAULT_APP_CONFIG };
  for (const key of KEYS) {
    if (given[key] !== undefined) {
      result[key] = checked(key, given[key]);
    }
  }
  return result as unknown as AppConfig;
}

export { loadAppConfig } from './load-app-config';
