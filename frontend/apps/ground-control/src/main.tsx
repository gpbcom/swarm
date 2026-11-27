import '@swarm/tokens/tokens.css';
import '@swarm/ui/styles.css';

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { I18nProvider } from '@swarm/i18n';

import { App } from './App';
import { loadAppConfig } from './config/app-config';

const container = document.querySelector<HTMLElement>('#root');
if (container === null) {
  throw new Error('The #root element is missing from index.html.');
}
const root = createRoot(container);

loadAppConfig()
  .then((config) => {
    root.render(
      <StrictMode>
        <I18nProvider language={undefined}>
          <App config={config} />
        </I18nProvider>
      </StrictMode>,
    );
  })
  .catch((error: unknown) => {
    console.error(error);
  });
