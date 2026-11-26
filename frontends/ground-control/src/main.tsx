import '@swarm/tokens/tokens.css';
import '@swarm/ui/styles.css';

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { I18nProvider } from '@swarm/i18n';

import { App } from './App';

const container = document.querySelector<HTMLElement>('#root');
if (container === null) {
  throw new Error('The #root element is missing from index.html.');
}

createRoot(container).render(
  <StrictMode>
    <I18nProvider language={undefined}>
      <App />
    </I18nProvider>
  </StrictMode>,
);
