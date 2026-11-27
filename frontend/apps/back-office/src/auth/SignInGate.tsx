import { useEffect, useState, type ReactNode } from 'react';
import type { UserManager } from 'oidc-client-ts';

import { createUserManager } from './oidc';
import { SessionProvider } from './SessionProvider';
import { sessionFromToken, type Session } from './session';

const CODE_PARAMETER = 'code';

export interface SignInGateProps {
  children: ReactNode;
  userManager?: UserManager;
}

async function resolveSession(userManager: UserManager): Promise<Session | null> {
  if (new URLSearchParams(window.location.search).has(CODE_PARAMETER)) {
    const returned = await userManager.signinRedirectCallback();
    window.history.replaceState({}, document.title, window.location.pathname);
    return sessionFromToken(returned.access_token);
  }
  const user = await userManager.getUser();
  if (user !== null && !user.expired) {
    return sessionFromToken(user.access_token);
  }
  await userManager.signinRedirect();
  return null;
}

export function SignInGate({ children, userManager }: SignInGateProps) {
  const [session, setSession] = useState<Session | null>(null);

  useEffect(() => {
    let active = true;
    const manager = userManager ?? createUserManager();
    void resolveSession(manager).then((resolved) => {
      if (active) {
        setSession(resolved);
      }
    });
    return () => {
      active = false;
    };
  }, [userManager]);

  if (session === null) {
    return null;
  }
  return <SessionProvider session={session}>{children}</SessionProvider>;
}
