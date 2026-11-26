import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Grid2, Mono, Muted, Row, Spacer, Stack } from '../../src/layout';

describe('layout helpers', () => {
  it.each([
    ['Row', Row, 'row'],
    ['Stack', Stack, 'stack'],
    ['Grid2', Grid2, 'grid-2'],
    ['Spacer', Spacer, 'spacer'],
  ])('%s renders a div with the class %s', (_name, Component, className) => {
    const { container } = render(<Component>content</Component>);
    const element = container.firstElementChild as HTMLElement;
    expect(element.tagName).toBe('DIV');
    expect(element.classList.contains(className)).toBe(true);
  });

  it.each([
    ['Row', Row],
    ['Stack', Stack],
    ['Grid2', Grid2],
    ['Spacer', Spacer],
  ])('%s renders its children', (_name, Component) => {
    const { getByText } = render(
      <Component>
        <b>child</b>
      </Component>,
    );
    expect(getByText('child')).toBeTruthy();
  });

  it.each([
    ['Muted', Muted, 'muted'],
    ['Mono', Mono, 'mono'],
  ])('%s renders a span with the class %s', (_name, Component, className) => {
    const { container, getByText } = render(<Component>text</Component>);
    const element = container.firstElementChild as HTMLElement;
    expect(element.tagName).toBe('SPAN');
    expect(element.classList.contains(className)).toBe(true);
    expect(getByText('text')).toBeTruthy();
  });
});
