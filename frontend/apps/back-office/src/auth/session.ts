export interface Session {
  accessToken: string;
  roles: readonly string[];
  operatorId: string | null;
}

export const SWARM_ADMINISTRATOR_ROLE = 'swarm_administrator';

interface TokenPayload {
  realm_access?: { roles?: unknown };
  operator_id?: unknown;
}

function readPayload(accessToken: string): TokenPayload {
  const part = accessToken.split('.')[1] ?? '';
  const base64 = part.replace(/-/g, '+').replace(/_/g, '/');
  const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=');
  const bytes = Uint8Array.from(atob(padded), (character) => character.charCodeAt(0));
  return JSON.parse(new TextDecoder().decode(bytes)) as TokenPayload;
}

/** Reads, without checking it, the roles and the Operator of an access token: the gateway checks it. */
export function sessionFromToken(accessToken: string): Session {
  const payload = readPayload(accessToken);
  const roles = payload.realm_access?.roles;
  const operatorId = payload.operator_id;
  return {
    accessToken,
    roles: Array.isArray(roles) ? roles.filter((role): role is string => typeof role === 'string') : [],
    operatorId: typeof operatorId === 'string' ? operatorId : null,
  };
}

export function isSwarmAdministrator(session: Session): boolean {
  return session.roles.includes(SWARM_ADMINISTRATOR_ROLE);
}
