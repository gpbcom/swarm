import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it } from 'vitest';

import { I18nProvider } from '@swarm/i18n';

import { GatewayProvider } from '../../src/api/GatewayProvider';
import { createBackOfficeGateway } from '../../src/api/gateway';
import { SessionProvider } from '../../src/auth/SessionProvider';
import { sessionFromToken } from '../../src/auth/session';
import { App } from '../../src/App';
import {
  ADMINISTRATOR_ROLE,
  BASE_URL,
  anOperator,
  createStandInGateway,
  tokenFor,
} from '../stand-ins/stand-in-gateway';
import type { StandInGateway, StandInOptions } from '../stand-ins/stand-in-gateway';

const NAME = 'Aerowing Services';
const NEXT = 'Next: first Mission planner ▶️';
const CREATE = 'Create the Operator and send the invitation';
const PLANNER_HEADING = '👥 First Mission planner of Aerowing Services';
const ENTRY_HEADING = '➕ Create an Operator';

function openApp(options: StandInOptions = {}): StandInGateway {
  const standIn = createStandInGateway(options);
  const token = tokenFor([ADMINISTRATOR_ROLE], null);
  const client = createBackOfficeGateway({ baseUrl: BASE_URL, accessToken: token, fetch: standIn.fetch });
  render(
    <I18nProvider language="en">
      <SessionProvider session={sessionFromToken(token)}>
        <GatewayProvider client={client}>
          <App />
        </GatewayProvider>
      </SessionProvider>
    </I18nProvider>,
  );
  return standIn;
}

async function enterOperator(name: string, jurisdiction: string | null): Promise<void> {
  const user = userEvent.setup();
  await screen.findByRole('heading', { name: ENTRY_HEADING });
  await user.type(screen.getByLabelText('Operator name'), name);
  if (jurisdiction !== null) {
    await user.click(screen.getByRole('checkbox', { name: jurisdiction }));
  }
  await user.click(screen.getByRole('button', { name: NEXT }));
}

async function invitePlanner(): Promise<void> {
  const user = userEvent.setup();
  await screen.findByRole('heading', { name: PLANNER_HEADING });
  await user.type(screen.getByLabelText('Name'), 'Léa Martin');
  await user.type(screen.getByLabelText('E-mail address'), 'lea.martin@aerowing.example');
  await user.click(screen.getByRole('button', { name: CREATE }));
}

describe('create an Operator wizard', () => {
  afterEach(cleanup);

  it('shows the entry of the Operator with its defaults', async () => {
    openApp();
    expect(await screen.findByRole('heading', { name: ENTRY_HEADING })).toBeTruthy();
    expect(screen.getByLabelText('Operator name')).toBeTruthy();
    expect(screen.getByText('Deployment')).toBeTruthy();
    expect(screen.getByRole('radio', { name: 'Cloud' })).toHaveProperty('checked', true);
    expect(screen.getByRole('radio', { name: 'On premises' })).toHaveProperty('checked', false);
    expect(screen.getByText('Jurisdictions')).toBeTruthy();
    expect(screen.getByRole('checkbox', { name: 'EU (EASA)' })).toBeTruthy();
    expect(screen.getByRole('checkbox', { name: 'US (FAA)' })).toBeTruthy();
    expect(screen.getByLabelText('LLM provider and models')).toBeTruthy();
    expect(screen.getByText(/Claude/)).toBeTruthy();
    expect(screen.getByText('🔏 Anchoring')).toBeTruthy();
    expect(screen.getByRole('radio', { name: 'Qualified timestamping authority (eIDAS, RFC 3161)' })).toHaveProperty(
      'checked',
      true,
    );
    expect(screen.getByRole('radio', { name: 'Public blockchain, through an aggregator' })).toBeTruthy();
    expect(screen.getByRole('radio', { name: 'No Anchoring: signed and chained only' })).toBeTruthy();
    expect(screen.getByRole('button', { name: NEXT })).toBeTruthy();
  });

  it('refuses a next step without a Jurisdiction and sends nothing', async () => {
    const standIn = openApp();
    await enterOperator(NAME, null);
    expect(await screen.findByText('❌ Operator not created.')).toBeTruthy();
    expect(screen.getByText('Choose at least one Jurisdiction: it is required.')).toBeTruthy();
    expect(screen.getByRole('heading', { name: ENTRY_HEADING })).toBeTruthy();
    expect(standIn.posts()).toHaveLength(0);
  });

  it('refuses the name of a listed Operator', async () => {
    openApp({ operators: [anOperator(NAME)] });
    await enterOperator(NAME, 'EU (EASA)');
    expect(await screen.findByText('An Operator named Aerowing Services already exists.')).toBeTruthy();
    expect(screen.getByRole('heading', { name: ENTRY_HEADING })).toBeTruthy();
  });

  it('refuses the name of a listed Operator whatever its case', async () => {
    openApp({ operators: [anOperator(NAME)] });
    await enterOperator('AEROWING services', 'EU (EASA)');
    expect(await screen.findByText(/already exists\./)).toBeTruthy();
    expect(screen.getByRole('heading', { name: ENTRY_HEADING })).toBeTruthy();
  });

  it('moves to the first Mission planner when the entry is valid', async () => {
    openApp();
    await enterOperator(NAME, 'EU (EASA)');
    expect(await screen.findByRole('heading', { name: PLANNER_HEADING })).toBeTruthy();
    expect(screen.getByLabelText('E-mail address')).toBeTruthy();
  });

  it('names the e-mail address as required and sends nothing without it', async () => {
    const standIn = openApp();
    const user = userEvent.setup();
    await enterOperator(NAME, 'EU (EASA)');
    await screen.findByRole('heading', { name: PLANNER_HEADING });
    await user.click(screen.getByRole('button', { name: CREATE }));
    expect(await screen.findByText(/E-mail address.*required/i)).toBeTruthy();
    expect(standIn.posts()).toHaveLength(0);
  });

  it('sends one POST with the entry, the bearer token and an idempotency key', async () => {
    const standIn = openApp();
    await enterOperator(NAME, 'EU (EASA)');
    await invitePlanner();
    await waitFor(() => {
      expect(standIn.posts()).toHaveLength(1);
    });
    const post = standIn.posts()[0];
    expect(post?.path).toBe('/v1/operators');
    expect(post?.headers.get('Authorization')).toMatch(/^Bearer .+/);
    expect(post?.headers.get('Idempotency-Key')).toBeTruthy();
    expect(post?.body).toEqual({
      name: NAME,
      deployment: 'cloud',
      jurisdictions: ['eu_easa'],
      llm_provider: 'claude',
      anchoring: 'qualified_timestamping',
      first_mission_planner_name: 'Léa Martin',
      first_mission_planner_email: 'lea.martin@aerowing.example',
    });
  });

  it('brings back the entry with the name error when the answer is a conflict', async () => {
    openApp({ postStatus: 409 });
    await enterOperator(NAME, 'EU (EASA)');
    await invitePlanner();
    expect(await screen.findByText('An Operator named Aerowing Services already exists.')).toBeTruthy();
    expect(screen.getByRole('heading', { name: ENTRY_HEADING })).toBeTruthy();
  });

  it('keeps the planner step and names the e-mail when the e-mail is already used', async () => {
    const standIn = openApp({ postStatus: 409, conflict: 'email' });
    await enterOperator(NAME, 'EU (EASA)');
    await invitePlanner();
    expect(
      await screen.findByText('E-mail address: lea.martin@aerowing.example is already used by another account.'),
    ).toBeTruthy();
    expect(screen.getByRole('heading', { name: PLANNER_HEADING })).toBeTruthy();
    expect(screen.queryByText('An Operator named Aerowing Services already exists.')).toBeNull();
    expect(standIn.posts()).toHaveLength(1);
  });

  it('sends the open-weight model for an Operator on premises with no explicit choice', async () => {
    const standIn = openApp();
    const user = userEvent.setup();
    await screen.findByRole('heading', { name: ENTRY_HEADING });
    await user.click(screen.getByRole('radio', { name: 'On premises' }));
    await enterOperator(NAME, 'EU (EASA)');
    await invitePlanner();
    await waitFor(() => {
      expect(standIn.posts()).toHaveLength(1);
    });
    expect(standIn.posts()[0]?.body?.deployment).toBe('on_premises');
    expect(standIn.posts()[0]?.body?.llm_provider).toBe('open_weight');
  });

  it('sends the provider the person chose, whatever the deployment', async () => {
    const standIn = openApp();
    const user = userEvent.setup();
    await screen.findByRole('heading', { name: ENTRY_HEADING });
    await user.click(screen.getByRole('radio', { name: 'On premises' }));
    await user.selectOptions(screen.getByLabelText('LLM provider and models'), 'claude');
    await enterOperator(NAME, 'EU (EASA)');
    await invitePlanner();
    await waitFor(() => {
      expect(standIn.posts()).toHaveLength(1);
    });
    expect(standIn.posts()[0]?.body?.llm_provider).toBe('claude');
  });
});
