import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

const SRC = join(import.meta.dirname, '..', 'src');
const TOKENS = join(import.meta.dirname, '..', '..', 'tokens', 'src', 'tokens.css');
const GROUPS = ['layout', 'controls', 'overlays', 'feedback', 'data', 'frames'];

function cssFiles(dir: string): string[] {
  const found: string[] = [];
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) {
      found.push(...cssFiles(path));
    } else if (name.endsWith('.css')) {
      found.push(path);
    }
  }
  return found;
}

function read(path: string): string {
  return readFileSync(path, 'utf-8');
}

function stripComments(css: string): string {
  return css.replace(/\/\*[\s\S]*?\*\//g, '');
}

describe('ui stylesheets', () => {
  it('has stylesheets under src', () => {
    expect(cssFiles(SRC).length).toBeGreaterThan(0);
  });

  it('holds no colour literal', () => {
    const colour = /#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(/;
    for (const file of cssFiles(SRC)) {
      expect(stripComments(read(file)), file).not.toMatch(colour);
    }
  });

  it('holds no font family that is not a font token', () => {
    for (const file of cssFiles(SRC)) {
      const css = stripComments(read(file));
      for (const match of css.matchAll(/font-family\s*:\s*([^;}]*)/g)) {
        expect(String(match[1]).trim(), file).toMatch(/^var\(--font-[a-z0-9-]+\)$/);
      }
    }
  });

  it('uses only variables defined in the tokens', () => {
    const defined = new Set(
      [...stripComments(read(TOKENS)).matchAll(/(--[a-z0-9-]+)\s*:/g)].map((m) => String(m[1])),
    );
    expect(defined.size).toBeGreaterThan(0);
    for (const file of cssFiles(SRC)) {
      const css = stripComments(read(file));
      for (const match of css.matchAll(/var\(\s*(--[a-z0-9-]+)/g)) {
        const name = String(match[1]);
        expect(defined.has(name), `${file} uses ${name}`).toBe(true);
      }
    }
  });

  it('imports base.css from styles.css', () => {
    expect(read(join(SRC, 'styles.css'))).toMatch(/@import\s+(url\()?['"]\.\/base\.css['"]/);
  });

  it.each(GROUPS)('imports the %s stylesheet from styles.css', (group) => {
    const target = `./${group}/${group}.css`;
    expect(read(join(SRC, 'styles.css'))).toContain(target);
  });

  it('sets the body background to the background token', () => {
    expect(stripComments(read(join(SRC, 'base.css')))).toMatch(
      /body\s*\{[^}]*background\s*:\s*var\(--color-background\)/,
    );
  });

  it('sets the body colour to the text token', () => {
    expect(stripComments(read(join(SRC, 'base.css')))).toMatch(
      /body\s*\{[^}]*[^-]color\s*:\s*var\(--color-text\)/,
    );
  });

  it('sets the body font family to the ui font token', () => {
    expect(stripComments(read(join(SRC, 'base.css')))).toMatch(
      /body\s*\{[^}]*font-family\s*:\s*var\(--font-ui\)/,
    );
  });
});
