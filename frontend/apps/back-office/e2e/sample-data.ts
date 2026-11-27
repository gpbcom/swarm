import type { Page, Route } from "@playwright/test";

export type SampleState = "a1" | "ko" | "a2" | "ok";

export const OPERATOR_NAME = "Aerowing Services";
export const PLANNER_NAME = "Léa Martin";
export const PLANNER_EMAIL = "lea.martin@aerowing.example";
export const ADMINISTRATOR_ROLE = "swarm_administrator";
export const SAMPLE_TIME = new Date("2026-12-03T10:00:00Z");

const DEPLOYMENT = "cloud";
const JURISDICTIONS = ["eu_easa"];
const LLM_PROVIDER = "claude";
const ANCHORING = "qualified_timestamping";
const CELL = "cell-eu-1";
const LANGUAGE = "en";
const OPERATOR_ID = "01930000-0000-7000-8000-0000000000a1";
const PLANNER_ID = "01930000-0000-7000-8000-0000000000b1";
const TAKEN_OPERATOR_ID = "01930000-0000-7000-8000-0000000000c1";
const ASSIGNED_AT = "2026-12-01T09:00:00Z";
const ACCESS_TOKEN_LIFETIME_S = 3600;
const AUTHORISATION_CODE = "sample-code";
const CLIENT_ID = "back-office";
const ADMINISTRATOR_ID = "01930000-0000-7000-8000-0000000000d1";

const PROBLEM_JSON = "application/problem+json";
const OPERATORS_PATH = "/v1/operators";
const GATEWAY_PATTERN = "**/v1/operators**";
const REALM_PATTERN = "**/realms/swarm/**";
const DISCOVERY_PATH = "/.well-known/openid-configuration";
const AUTHORISE_PATH = "/protocol/openid-connect/auth";
const TOKEN_PATH = "/protocol/openid-connect/token";
const CERTS_PATH = "/protocol/openid-connect/certs";
const REALM_PATH = "/realms/swarm";
const OPTIONS = "OPTIONS";
const GET = "GET";
const POST = "POST";
const NO_CONTENT = 204;
const CREATED = 201;
const CONFLICT = 409;
const UNPROCESSABLE = 422;
const FOUND = 302;
const NOT_FOUND = 404;
const OK_STATUS = 200;

const CORS_HEADERS: Record<string, string> = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "*",
  "access-control-allow-methods": "GET, POST, OPTIONS",
};

interface Entry {
  operator: {
    id: string;
    name: string;
    deployment: string;
    jurisdictions: string[];
    llm_provider: string;
    anchoring: string;
  };
  cell_assignment: { operator_id: string; cell: string; assigned_at: string };
}

interface CreationBody {
  name?: string;
  jurisdictions?: string[];
}

function entryFor(id: string): Entry {
  return {
    operator: {
      id,
      name: OPERATOR_NAME,
      deployment: DEPLOYMENT,
      jurisdictions: JURISDICTIONS,
      llm_provider: LLM_PROVIDER,
      anchoring: ANCHORING,
    },
    cell_assignment: { operator_id: id, cell: CELL, assigned_at: ASSIGNED_AT },
  };
}

function encode(value: object): string {
  return Buffer.from(JSON.stringify(value)).toString("base64url");
}

function token(claims: object): string {
  return `${encode({ alg: "none", typ: "JWT" })}.${encode(claims)}.signature`;
}

/** The claims Keycloak puts in every token of the realm: the oidc-client-ts callback refuses an ID token without `sub`. */
function standardClaims(issuer: string): object {
  const issuedAt = Math.floor(SAMPLE_TIME.getTime() / 1000);
  return {
    iss: issuer,
    sub: ADMINISTRATOR_ID,
    aud: CLIENT_ID,
    azp: CLIENT_ID,
    iat: issuedAt,
    exp: issuedAt + ACCESS_TOKEN_LIFETIME_S,
  };
}

function accessToken(issuer: string): string {
  return token({ ...standardClaims(issuer), realm_access: { roles: [ADMINISTRATOR_ROLE] } });
}

function idToken(issuer: string): string {
  return token({ ...standardClaims(issuer), typ: "ID" });
}

async function answerIdentity(route: Route): Promise<void> {
  const request = route.request();
  const url = new URL(request.url());
  const realm = `${url.origin}${REALM_PATH}`;
  if (request.method() === OPTIONS) {
    await route.fulfill({ status: NO_CONTENT, headers: CORS_HEADERS });
  } else if (url.pathname.endsWith(DISCOVERY_PATH)) {
    await route.fulfill({
      headers: CORS_HEADERS,
      json: {
        issuer: realm,
        authorization_endpoint: `${realm}${AUTHORISE_PATH}`,
        token_endpoint: `${realm}${TOKEN_PATH}`,
        jwks_uri: `${realm}${CERTS_PATH}`,
      },
    });
  } else if (url.pathname.endsWith(AUTHORISE_PATH)) {
    const back = new URL(url.searchParams.get("redirect_uri") ?? "/");
    back.searchParams.set("code", AUTHORISATION_CODE);
    back.searchParams.set("state", url.searchParams.get("state") ?? "");
    await route.fulfill({ status: FOUND, headers: { location: back.toString() } });
  } else if (url.pathname.endsWith(TOKEN_PATH)) {
    await route.fulfill({
      headers: CORS_HEADERS,
      json: {
        access_token: accessToken(realm),
        id_token: idToken(realm),
        token_type: "Bearer",
        expires_in: ACCESS_TOKEN_LIFETIME_S,
        scope: "openid",
      },
    });
  } else {
    await route.fulfill({ status: OK_STATUS, headers: CORS_HEADERS, json: { keys: [] } });
  }
}

/**
 * Stub every request of the Back office to the gateway and to the identity provider, so that no backend runs, and fix
 * the clock. The directory holds the taken name in state `ko`, and the creation answers as the gateway does.
 */
export async function installSampleData(page: Page, state: SampleState): Promise<void> {
  await page.clock.setFixedTime(SAMPLE_TIME);
  const directory: Entry[] = state === "ko" ? [entryFor(TAKEN_OPERATOR_ID)] : [];

  await page.route(REALM_PATTERN, answerIdentity);
  await page.route(GATEWAY_PATTERN, async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    if (request.method() === OPTIONS) {
      await route.fulfill({ status: NO_CONTENT, headers: CORS_HEADERS });
    } else if (request.method() === GET && path === OPERATORS_PATH) {
      await route.fulfill({ headers: CORS_HEADERS, json: directory });
    } else if (request.method() === POST && path === OPERATORS_PATH) {
      const body = request.postDataJSON() as CreationBody;
      if (directory.length > 0) {
        await route.fulfill({
          status: CONFLICT,
          headers: { ...CORS_HEADERS, "content-type": PROBLEM_JSON },
          body: JSON.stringify({ title: "An Operator with that name already exists.", status: CONFLICT }),
        });
      } else if ((body.jurisdictions ?? []).length === 0) {
        await route.fulfill({
          status: UNPROCESSABLE,
          headers: { ...CORS_HEADERS, "content-type": PROBLEM_JSON },
          body: JSON.stringify({ title: "A Jurisdiction is required.", status: UNPROCESSABLE }),
        });
      } else {
        const created = entryFor(OPERATOR_ID);
        directory.push(created);
        await route.fulfill({
          status: CREATED,
          headers: CORS_HEADERS,
          json: {
            ...created,
            first_mission_planner: {
              id: PLANNER_ID,
              operator_id: OPERATOR_ID,
              name: PLANNER_NAME,
              email: PLANNER_EMAIL,
              language: LANGUAGE,
            },
          },
        });
      }
    } else {
      await route.fulfill({
        status: NOT_FOUND,
        headers: { ...CORS_HEADERS, "content-type": PROBLEM_JSON },
        body: JSON.stringify({ title: "Not found", status: NOT_FOUND }),
      });
    }
  });
}
