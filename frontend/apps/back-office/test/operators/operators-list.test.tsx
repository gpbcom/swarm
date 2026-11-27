import { cleanup, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it } from 'vitest';

import { I18nProvider } from '@swarm/i18n';

import { GatewayProvider } from '../../src/api/GatewayProvider';
import { createBackOfficeGateway } from '../../src/api/gateway';
import { SessionProvider } from '../../src/auth/SessionProvider';
import { sessionFromToken } from '../../src/auth/session';
import { App } from '../../src/App';
import { ADMINISTRATOR_ROLE, BASE_URL, CELL, createStandInGateway, tokenFor } from '../stand-ins/stand-in-gateway';

const NAME = 'Aerowing Services';
const COLUMNS: string[] = ['Operator', 'Deployment', 'Jurisdictions', 'Anchoring', 'Cell', 'State'];

async function createAerowing(): Promise<void> {
  const standIn = createStandInGateway();
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
  const user = userEvent.setup();
  await screen.findByRole('heading', { name: '➕ Create an Operator' });
  await user.type(screen.getByLabelText('Operator name'), NAME);
  await user.click(screen.getByRole('checkbox', { name: 'EU (EASA)' }));
  await user.click(screen.getByRole('button', { name: 'Next: first Mission planner ▶️' }));
  await screen.findByRole('heading', { name: '👥 First Mission planner of Aerowing Services' });
  await user.type(screen.getByLabelText('Name'), 'Léa Martin');
  await user.type(screen.getByLabelText('E-mail address'), 'lea.martin@aerowing.example');
  await user.click(screen.getByRole('button', { name: 'Create the Operator and send the invitation' }));
}

describe('operators list', () => {
  afterEach(cleanup);

  it('confirms the creation and the isolation of the Operator', async () => {
    await createAerowing();
    expect(
      await screen.findByText('✅ Aerowing Services created. Its data is isolated: no other Operator can see it.'),
    ).toBeTruthy();
  });

  it('shows the Operators table with its columns', async () => {
    await createAerowing();
    expect(await screen.findByRole('heading', { name: '🗃️ Operators' })).toBeTruthy();
    const headers = screen.getAllByRole('columnheader').map((header) => header.textContent.trim());
    expect(headers).toEqual(COLUMNS);
  });

  it('lists the created Operator with its cell', async () => {
    await createAerowing();
    const cell = await screen.findByRole('cell', { name: NAME });
    const row = cell.closest('tr');
    expect(row).not.toBeNull();
    expect(within(row as HTMLElement).getByText(CELL)).toBeTruthy();
  });
});
