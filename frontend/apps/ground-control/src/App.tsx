import { GroundControlFrame } from '@swarm/ui';
import { LANGUAGE_NAMES, useLanguage } from '@swarm/i18n';
import { useIntl } from 'react-intl';
import type { ReactNode } from 'react';

import type { AppConfig } from './config/app-config';
import { FlightView } from './flight/FlightView';
import type { LoadMap } from './flight/FlightView';
import type { LiveClientLike } from './flight/squad-feed';

export interface AppProps {
  config: AppConfig;
  createLiveClient?: () => LiveClientLike;
  loadMap?: LoadMap;
}

export function App({ config, createLiveClient, loadMap }: AppProps): ReactNode {
  const intl = useIntl();
  const { language } = useLanguage();
  const statusItems = [
    intl.formatMessage({ id: 'status.language' }, { language: LANGUAGE_NAMES[language] }),
  ];
  return (
    <GroundControlFrame statusItems={statusItems} onHold={() => undefined} onAbort={() => undefined}>
      <FlightView
        config={config}
        {...(createLiveClient ? { createLiveClient } : {})}
        {...(loadMap ? { loadMap } : {})}
      />
    </GroundControlFrame>
  );
}
