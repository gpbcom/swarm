import { AppConfigError, DEFAULT_APP_CONFIG, parseAppConfig, type AppConfig } from './app-config';

export type ConfigFetch = (url: string) => Promise<Response>;

const CONFIG_URL = 'config.json';
const NOT_FOUND = 404;

export async function loadAppConfig(fetcher: ConfigFetch = (url) => fetch(url)): Promise<AppConfig> {
  let response: Response;
  try {
    response = await fetcher(CONFIG_URL);
  } catch {
    throw new AppConfigError('The configuration could not be requested.');
  }
  if (response.status === NOT_FOUND) {
    return { ...DEFAULT_APP_CONFIG };
  }
  if (!response.ok) {
    throw new AppConfigError(`The configuration request failed with status ${String(response.status)}.`);
  }
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    throw new AppConfigError('The configuration is not valid JSON.');
  }
  return parseAppConfig(body);
}
