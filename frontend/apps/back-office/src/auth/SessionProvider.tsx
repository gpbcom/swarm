import { createContext, useContext, type ReactNode } from 'react';

import type { Session } from './session';

const SessionContext = createContext<Session | null>(null);

export interface SessionProviderProps {
  session: Session;
  children: ReactNode;
}

export function SessionProvider({ session, children }: SessionProviderProps) {
  return <SessionContext.Provider value={session}>{children}</SessionContext.Provider>;
}

export function useSession(): Session {
  const session = useContext(SessionContext);
  if (session === null) {
    throw new Error('useSession must be used inside a SessionProvider.');
  }
  return session;
}
