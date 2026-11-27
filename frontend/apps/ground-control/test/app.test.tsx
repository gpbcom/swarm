import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

import { cleanup, fireEvent, render as renderBare, screen } from '@testing-library/react';
import type { RenderResult } from '@testing-library/react';
import type { ReactElement } from 'react';
import { afterEach, describe, expect, it } from 'vitest';

import { I18nProvider } from '@swarm/i18n';

import { App } from '../src/App';
import { DEFAULT_APP_CONFIG } from '../src/config/app-config';
import { FakeLiveClient, FakeSquadMapModule, MAP_LABEL, MISSION_ID } from './flight/fakes';

function render(ui: ReactElement): RenderResult {
  return renderBare(<I18nProvider language="en">{ui}</I18nProvider>);
}

function renderApp(missionId: string | null = null): { result: RenderResult; client: FakeLiveClient } {
  const client = new FakeLiveClient();
  const maps = new FakeSquadMapModule();
  const config = { ...DEFAULT_APP_CONFIG, missionId };
  const result = render(<App config={config} createLiveClient={() => client} loadMap={maps.loadMap} />);
  return { result, client };
}

const APP_ROOT = resolve(__dirname, '..');
const PART = 'Ground control';
const NAV_ITEMS: string[] = ['🛰️ Flight', '📋 Pre-flight', '🛸 Squad', '🎥 Video', '📼 Debrief', '🔧 Settings'];

function navTexts(container: HTMLElement): string[] {
  return Array.from(container.querySelectorAll('.nav-item')).map((item) => item.textContent.trim());
}

describe('ground-control shell', () => {
  afterEach(cleanup);

  it('shows the title bar with the Swarm name', () => {
    const { container } = renderApp().result;
    const bar = container.querySelector('header.titlebar');
    expect(bar).not.toBeNull();
    expect(bar?.textContent).toContain('⚙️ Swarm');
  });

  it('shows the part name in the title bar', () => {
    const { container } = renderApp().result;
    expect(container.querySelector('header.titlebar')?.textContent).toContain(PART);
  });

  it('marks the first side bar item as active', () => {
    const { container } = renderApp().result;
    const active = container.querySelectorAll('.nav-item.active');
    expect(active).toHaveLength(1);
    expect(active[0]?.textContent.trim()).toBe(NAV_ITEMS[0]);
  });

  it('shows the side bar items of the part in order', () => {
    const { container } = renderApp().result;
    expect(navTexts(container)).toEqual(NAV_ITEMS);
  });

  it('shows the Hold the Squad button', () => {
    const { container } = renderApp().result;
    const labels = Array.from(container.querySelectorAll('button')).map((b) => b.textContent.trim());
    expect(labels).toContain('✋ Hold the Squad');
  });

  it('shows the Abort button', () => {
    const { container } = renderApp().result;
    const labels = Array.from(container.querySelectorAll('button')).map((b) => b.textContent.trim());
    expect(labels).toContain('🛑 Abort');
  });

  it('shows the map of the Squad as one labelled region in the content area', async () => {
    const { result } = renderApp();
    const region = await screen.findByRole('region', { name: MAP_LABEL });
    const content = result.container.querySelector('main.content');
    expect(content).not.toBeNull();
    expect(content?.contains(region)).toBe(true);
    expect(content?.querySelectorAll('[role="region"]')).toHaveLength(1);
  });

  it('shows Hold the Squad and Abort in the title bar', () => {
    const { result } = renderApp();
    const labels = Array.from(result.container.querySelectorAll('header.titlebar button')).map((b) =>
      b.textContent.trim(),
    );
    expect(labels).toContain('✋ Hold the Squad');
    expect(labels).toContain('🛑 Abort');
  });

  it('does nothing yet when Hold the Squad and Abort are clicked', async () => {
    const { result, client } = renderApp(MISSION_ID);
    await screen.findByRole('region', { name: MAP_LABEL });
    const connects = client.connects.length;
    for (const button of Array.from(result.container.querySelectorAll('header.titlebar button'))) {
      expect(() => fireEvent.click(button)).not.toThrow();
    }
    expect(client.connects).toHaveLength(connects);
    expect(client.closes).toBe(0);
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
