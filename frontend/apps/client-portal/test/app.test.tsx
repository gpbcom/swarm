import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

import { cleanup, render as renderBare } from '@testing-library/react';
import type { RenderResult } from '@testing-library/react';
import type { ReactElement } from 'react';
import { afterEach, describe, expect, it } from 'vitest';

import { I18nProvider } from '@swarm/i18n';

import { App } from '../src/App';

function render(ui: ReactElement): RenderResult {
  return renderBare(<I18nProvider language="en">{ui}</I18nProvider>);
}

const APP_ROOT = resolve(__dirname, '..');
const PART = 'Client portal';
const NAV_ITEMS: string[] = ['🗺️ Missions', '➕ Order', '📦 Deliverables', '🧾 Scorecards'];

function navTexts(container: HTMLElement): string[] {
  return Array.from(container.querySelectorAll('.nav-item')).map((item) => item.textContent.trim());
}

describe('client-portal shell', () => {
  afterEach(cleanup);

  it('shows the title bar with the Swarm name', () => {
    const { container } = render(<App />);
    const bar = container.querySelector('header.titlebar');
    expect(bar).not.toBeNull();
    expect(bar?.textContent).toContain('⚙️ Swarm');
  });

  it('shows the part name in the title bar', () => {
    const { container } = render(<App />);
    expect(container.querySelector('header.titlebar')?.textContent).toContain(PART);
  });

  it('marks the first side bar item as active', () => {
    const { container } = render(<App />);
    const active = container.querySelectorAll('.nav-item.active');
    expect(active).toHaveLength(1);
    expect(active[0]?.textContent.trim()).toBe(NAV_ITEMS[0]);
  });

  it('shows the side bar items of the part in order', () => {
    const { container } = render(<App />);
    expect(navTexts(container)).toEqual(NAV_ITEMS);
  });

  it('has no Alarms item because nobody is signed in', () => {
    const { container } = render(<App />);
    expect(navTexts(container).some((text) => text.includes('🔔 Alarms'))).toBe(false);
  });

  it('shows no screen in the content area', () => {
    const { container } = render(<App />);
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
