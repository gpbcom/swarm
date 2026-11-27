import { UserManager, WebStorageStateStore } from 'oidc-client-ts';

import { config } from '../config';

const CODE_RESPONSE_TYPE = 'code';
const SCOPE = 'openid';
const CALLBACK_PATH = '/';

/** The public client `back-office` of the realm `swarm`: authorisation code flow with PKCE (S256). */
export function createUserManager(origin: string = window.location.origin): UserManager {
  return new UserManager({
    authority: `${config.identityUrl}/realms/${config.realm}`,
    client_id: config.clientId,
    redirect_uri: `${origin}${CALLBACK_PATH}`,
    response_type: CODE_RESPONSE_TYPE,
    scope: SCOPE,
    userStore: new WebStorageStateStore({ store: window.sessionStorage }),
  });
}
