import { createGatewayClient } from '@swarm/api-client';

export type GatewayClient = ReturnType<typeof createGatewayClient>;

export interface BackOfficeGatewayOptions {
  baseUrl: string;
  accessToken: string;
  fetch?: typeof fetch;
}

const AUTHORIZATION = 'Authorization';
const IDEMPOTENCY_KEY = 'Idempotency-Key';
const POST = 'POST';

/** A gateway client that sends the bearer token on every request and a fresh Idempotency-Key on every POST. */
export function createBackOfficeGateway(options: BackOfficeGatewayOptions): GatewayClient {
  const client = createGatewayClient(
    options.fetch === undefined ? { baseUrl: options.baseUrl } : { baseUrl: options.baseUrl, fetch: options.fetch },
  );
  client.use({
    onRequest({ request }) {
      request.headers.set(AUTHORIZATION, `Bearer ${options.accessToken}`);
      if (request.method === POST) {
        request.headers.set(IDEMPOTENCY_KEY, crypto.randomUUID());
      }
      return request;
    },
  });
  return client;
}
