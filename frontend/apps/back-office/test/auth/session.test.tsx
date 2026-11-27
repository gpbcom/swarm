import { describe, expect, it } from 'vitest';

import { isSwarmAdministrator, sessionFromToken } from '../../src/auth/session';
import { ADMINISTRATOR_ROLE, PLANNER_ROLE, tokenFor } from '../stand-ins/stand-in-gateway';

describe('session', () => {
  it('reads the roles and the Operator from the payload of the token', () => {
    const token = tokenFor([PLANNER_ROLE], 'op-1');
    const session = sessionFromToken(token);
    expect(session.accessToken).toBe(token);
    expect(session.roles).toEqual([PLANNER_ROLE]);
    expect(session.operatorId).toBe('op-1');
  });

  it('has no Operator when the token carries none', () => {
    expect(sessionFromToken(tokenFor([ADMINISTRATOR_ROLE], null)).operatorId).toBeNull();
  });

  it('recognises a Swarm administrator by her role', () => {
    expect(isSwarmAdministrator(sessionFromToken(tokenFor([ADMINISTRATOR_ROLE], null)))).toBe(true);
  });

  it('does not take a Mission planner for a Swarm administrator', () => {
    expect(isSwarmAdministrator(sessionFromToken(tokenFor([PLANNER_ROLE], 'op-1')))).toBe(false);
  });
});
