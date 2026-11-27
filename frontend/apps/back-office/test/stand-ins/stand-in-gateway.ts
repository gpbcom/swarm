export interface StandInOperator {
  id: string;
  name: string;
  deployment: 'cloud' | 'on_premises';
  jurisdictions: string[];
  llm_provider: 'claude' | 'open_weight';
  anchoring: 'qualified_timestamping' | 'public_blockchain' | 'none';
}

export interface StandInCellAssignment {
  operator_id: string;
  cell: string;
  assigned_at: string;
}

export interface StandInListed {
  operator: StandInOperator;
  cell_assignment: StandInCellAssignment;
}

export interface StandInEntry {
  name: string;
  deployment: string;
  jurisdictions: string[];
  llm_provider: string;
  anchoring: string;
  first_mission_planner_name: string;
  first_mission_planner_email: string;
}

export interface RecordedRequest {
  method: string;
  url: string;
  path: string;
  headers: Headers;
  body: StandInEntry | null;
}

export interface StandInOptions {
  operators?: StandInListed[];
  postStatus?: 201 | 409 | 422;
  /** What a 409 means: the name is taken (the directory then lists it) or the planner's e-mail is. */
  conflict?: 'name' | 'email';
}

export interface StandInGateway {
  fetch: typeof fetch;
  requests: RecordedRequest[];
  posts: () => RecordedRequest[];
}

export const BASE_URL = 'http://gateway.test';
export const CELL = 'cell-eu-1';
export const ADMINISTRATOR_ROLE = 'swarm_administrator';
export const PLANNER_ROLE = 'mission_planner';

export function anOperator(name: string, id = 'op-existing'): StandInListed {
  return {
    operator: {
      id,
      name,
      deployment: 'cloud',
      jurisdictions: ['eu_easa'],
      llm_provider: 'claude',
      anchoring: 'qualified_timestamping',
    },
    cell_assignment: { operator_id: id, cell: CELL, assigned_at: '2026-11-27T10:00:00Z' },
  };
}

export function tokenFor(roles: string[], operatorId: string | null): string {
  const encode = (value: object): string =>
    btoa(JSON.stringify(value)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  const payload: Record<string, object | string> = { realm_access: { roles } };
  if (operatorId !== null) {
    payload['operator_id'] = operatorId;
  }
  return `${encode({ alg: 'none', typ: 'JWT' })}.${encode(payload)}.signature`;
}

function answer(status: number, body: object, contentType = 'application/json'): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': contentType } });
}

export function createStandInGateway(options: StandInOptions = {}): StandInGateway {
  const stored: StandInListed[] = [...(options.operators ?? [])];
  const requests: RecordedRequest[] = [];
  const postStatus = options.postStatus ?? 201;

  const standInFetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const request = new Request(input, init);
    const url = new URL(request.url);
    const text = await request.clone().text();
    const body = text === '' ? null : (JSON.parse(text) as StandInEntry);
    requests.push({ method: request.method, url: request.url, path: url.pathname, headers: request.headers, body });

    if (request.method === 'GET' && url.pathname === '/v1/operators') {
      return answer(200, stored);
    }
    if (request.method === 'GET' && url.pathname.startsWith('/v1/operators/')) {
      const id = url.pathname.slice('/v1/operators/'.length);
      const found = stored.find((entry) => entry.operator.id === id);
      return found
        ? answer(200, found.operator)
        : answer(404, { title: 'Not found', status: 404 }, 'application/problem+json');
    }
    if (request.method === 'POST' && url.pathname === '/v1/operators' && body !== null) {
      if (postStatus !== 201) {
        if (postStatus === 409 && (options.conflict ?? 'name') === 'name') {
          stored.push(anOperator(body.name, 'op-concurrent'));
        }
        return answer(
          postStatus,
          { type: 'about:blank', title: 'Operator not created', status: postStatus, detail: body.name },
          'application/problem+json',
        );
      }
      const created = anOperator(body.name, 'op-new');
      created.operator = {
        ...created.operator,
        deployment: body.deployment as StandInOperator['deployment'],
        jurisdictions: body.jurisdictions,
        llm_provider: body.llm_provider as StandInOperator['llm_provider'],
        anchoring: body.anchoring as StandInOperator['anchoring'],
      };
      stored.push(created);
      return answer(201, {
        ...created,
        first_mission_planner: {
          id: 'person-new',
          operator_id: 'op-new',
          name: body.first_mission_planner_name,
          email: body.first_mission_planner_email,
          language: 'en',
        },
      });
    }
    return answer(404, { title: 'Not found', status: 404 }, 'application/problem+json');
  };

  return {
    fetch: standInFetch,
    requests,
    posts: () => requests.filter((entry) => entry.method === 'POST'),
  };
}
