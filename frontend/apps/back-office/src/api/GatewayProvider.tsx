import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createContext, useContext, useState, type ReactNode } from 'react';

import type { GatewayClient } from './gateway';

const GatewayContext = createContext<GatewayClient | null>(null);

export interface GatewayProviderProps {
  client: GatewayClient;
  children: ReactNode;
}

export function GatewayProvider({ client, children }: GatewayProviderProps) {
  const [queryClient] = useState(() => new QueryClient());
  return (
    <GatewayContext.Provider value={client}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </GatewayContext.Provider>
  );
}

export function useGateway(): GatewayClient {
  const client = useContext(GatewayContext);
  if (client === null) {
    throw new Error('useGateway must be used inside a GatewayProvider.');
  }
  return client;
}
