export interface BackOfficeConfig {
  identityUrl: string;
  gatewayUrl: string;
  clientId: string;
  realm: string;
}

const DEFAULT_IDENTITY_URL = 'http://localhost:8080';
const DEFAULT_GATEWAY_URL = 'http://localhost:8000';

export const config: BackOfficeConfig = {
  identityUrl: import.meta.env.VITE_SWARM_IDENTITY_URL ?? DEFAULT_IDENTITY_URL,
  gatewayUrl: import.meta.env.VITE_SWARM_GATEWAY_URL ?? DEFAULT_GATEWAY_URL,
  clientId: 'back-office',
  realm: 'swarm',
};
