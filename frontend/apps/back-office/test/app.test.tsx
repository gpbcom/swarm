import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

import { cleanup, render as renderBare, waitFor } from '@testing-library/react';
import type { RenderResult } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';

import { I18nProvider } from '@swarm/i18n';

import { GatewayProvider } from '../src/api/GatewayProvider';
import { createBackOfficeGateway } from '../src/api/gateway';
import { SessionProvider } from '../src/auth/SessionProvider';
import { sessionFromToken } from '../src/auth/session';
import { App } from '../src/App';
import {
  ADMINISTRATOR_ROLE,
  BASE_URL,
  PLANNER_ROLE,
  anOperator,
  createStandInGateway,
  tokenFor,
} from './stand-ins/stand-in-gateway';

const OPERATOR_NAME = 'Aerowing Services';
const OPERATOR_ID = 'op-1';

function renderAs(roles: string[], operatorId: string | null): RenderResult {
  const standIn = createStandInGateway({ operators: [anOperator(OPERATOR_NAME, OPERATOR_ID)] });
  const token = tokenFor(roles, operatorId);
  const client = createBackOfficeGateway({ baseUrl: BASE_URL, accessToken: token, fetch: standIn.fetch });
  return renderBare(
    <I18nProvider language="en">
      <SessionProvider session={sessionFromToken(token)}>
        <GatewayProvider client={client}>
          <App />
        </GatewayProvider>
      </SessionProvider>
    </I18nProvider>,
  );
}

const APP_ROOT = resolve(__dirname, '..');
const PART = 'Back office';
const NAV_ITEMS: string[] = ['🛸 Fleet', '📜 Authorisations', '📦 Deliverables', '🔏 Evidence', '👥 People', '🔧 Settings'];
const SWARM_ITEMS: string[] = ['➕ Operators', '👥 People', '🔧 Settings'];

function navTexts(container: HTMLElement): string[] {
  return Array.from(container.querySelectorAll('.nav-item')).map((item) => item.textContent.trim());
}

describe('back-office shell', () => {
  afterEach(cleanup);

  it('shows the title bar with the Swarm name', () => {
    const { container } = renderAs([PLANNER_ROLE], OPERATOR_ID);
    const bar = container.querySelector('header.titlebar');
    expect(bar).not.toBeNull();
    expect(bar?.textContent).toContain('⚙️ Swarm');
  });

  it('shows the part name in the title bar', () => {
    const { container } = renderAs([PLANNER_ROLE], OPERATOR_ID);
    expect(container.querySelector('header.titlebar')?.textContent).toContain(PART);
  });

  it('shows the name of her Operator in the title bar, read from the gateway', async () => {
    const { container } = renderAs([PLANNER_ROLE], OPERATOR_ID);
    await waitFor(() => {
      expect(container.querySelector("header.titlebar")?.textContent).toContain(OPERATOR_NAME);
    });
  });

  it('marks the first side bar item as active', () => {
    const { container } = renderAs([PLANNER_ROLE], OPERATOR_ID);
    const active = container.querySelectorAll('.nav-item.active');
    expect(active).toHaveLength(1);
    expect(active[0]?.textContent.trim()).toBe(NAV_ITEMS[0]);
  });

  it('shows the six side bar items of the part to a person of an Operator', () => {
    const { container } = renderAs([PLANNER_ROLE], OPERATOR_ID);
    expect(navTexts(container)).toEqual(NAV_ITEMS);
  });

  it('shows a Swarm administrator the three Swarm administration items, Operators active', () => {
    const { container } = renderAs([ADMINISTRATOR_ROLE], null);
    expect(navTexts(container)).toEqual(SWARM_ITEMS);
    expect(container.querySelector('.nav-item.active')?.textContent.trim()).toBe(SWARM_ITEMS[0]);
  });

  it('shows no screen in the content area of a person of an Operator', () => {
    const { container } = renderAs([PLANNER_ROLE], OPERATOR_ID);
    const content = container.querySelector('main.content');
    expect(content).not.toBeNull();
    expect(content?.children).toHaveLength(0);
    expect((content?.textContent ?? '').trim()).toBe('');
  });

  it('loads the tokens and the components styles and mounts into the root', () => {
    const source = readFileSync(resolve(APP_ROOT, 'src/main.tsx'), 'utf-8');
    expect(source).toContain('@swarm/tokens/tokens.css');
    expect(source).toContain('@swarm/ui/styles.css');
    expect(source).toContain('#root');
  });

  it('declares both colour schemes, English, a root and its title in the page', () => {
    const html = readFileSync(resolve(APP_ROOT, 'index.html'), 'utf-8');
    expect(html).toMatch(/<meta\s+name="color-scheme"\s+content="light dark"/);
    expect(html).toMatch(/<html[^>]*lang="en"/);
    expect(html).toMatch(/<div\s+id="root"/);
    expect(html).toContain('<title>⚙️ Swarm · ' + PART + '</title>');
  });

  it('has a dark mode block in the shared tokens', () => {
    const css = readFileSync(resolve(APP_ROOT, '../../packages/tokens/src/tokens.css'), 'utf-8');
    expect(css).toContain('@media (prefers-color-scheme: dark)');
  });
});
