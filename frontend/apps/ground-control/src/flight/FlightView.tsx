import { lazy, Suspense, useEffect, useMemo, useState } from 'react';
import type { ComponentType, ReactNode } from 'react';
import { useIntl } from 'react-intl';

import { LatencyHistogram, LatencyReporter, LiveClient, TELEMETRY_METRICS } from '@swarm/live';
import type { SquadSnapshot } from '@swarm/live';
import '@swarm/maps/styles.css';

import type { AppConfig } from '../config/app-config';
import { SquadFeed } from './squad-feed';
import type { LiveClientLike } from './squad-feed';
import './flight-view.css';

export interface MapSource {
  current(): SquadSnapshot | null;
  subscribe(listener: () => void): () => void;
}

export interface MapProps {
  tilesUrl: string;
  label: string;
  source: MapSource;
  onDrawn?: (data: SquadSnapshot, drawnAtMs: number) => void;
}

export interface MapModule {
  SquadMap: ComponentType<MapProps>;
}

export type LoadMap = () => Promise<MapModule>;

export interface FlightViewProps {
  config: AppConfig;
  createLiveClient?: () => LiveClientLike;
  loadMap?: LoadMap;
}

const COUNT_REFRESH_MS = 250;

const defaultLoadMap: LoadMap = () => import('@swarm/maps');
const defaultCreateLiveClient = (): LiveClientLike => new LiveClient();

export function FlightView({
  config,
  createLiveClient = defaultCreateLiveClient,
  loadMap = defaultLoadMap,
}: FlightViewProps): ReactNode {
  const intl = useIntl();
  const [droneToScreen] = useState(() => new LatencyHistogram());
  const [frameToPixels] = useState(() => new LatencyHistogram());
  const feed = useMemo(
    () => new SquadFeed(createLiveClient(), { droneToScreen, frameToPixels }),
    [createLiveClient, droneToScreen, frameToPixels],
  );
  const SquadMapView = useMemo(
    () => lazy(() => loadMap().then((module) => ({ default: module.SquadMap }))),
    [loadMap],
  );
  const [droneCount, setDroneCount] = useState(0);
  const tilesUrl = new URL(config.tilesUrl, document.baseURI).href;

  useEffect(() => {
    if (config.missionId === null) {
      return undefined;
    }
    let timer: ReturnType<typeof setTimeout> | null = null;
    const unsubscribe = feed.subscribe(() => {
      timer ??= setTimeout(() => {
        timer = null;
        setDroneCount(feed.count);
      }, COUNT_REFRESH_MS);
    });
    feed.start(config.liveUrl, config.missionId);
    return () => {
      unsubscribe();
      if (timer !== null) clearTimeout(timer);
      feed.stop();
    };
  }, [feed, config.liveUrl, config.missionId]);

  useEffect(() => {
    if (config.metricsUrl === null) {
      return undefined;
    }
    const reporter = new LatencyReporter({
      url: config.metricsUrl,
      intervalS: config.metricsIntervalS,
      missionId: config.missionId,
      cell: config.cell,
      path: config.livePath,
      histograms: {
        [TELEMETRY_METRICS.droneToScreen]: droneToScreen,
        [TELEMETRY_METRICS.frameToPixels]: frameToPixels,
      },
    });
    reporter.start();
    return () => {
      reporter.stop();
    };
  }, [
    config.metricsUrl,
    config.metricsIntervalS,
    config.missionId,
    config.cell,
    config.livePath,
    droneToScreen,
    frameToPixels,
  ]);

  return (
    <section className="flight-map" data-drone-count={droneCount}>
      <Suspense fallback={null}>
        <SquadMapView
          tilesUrl={tilesUrl}
          label={intl.formatMessage({ id: 'flight.map.label' })}
          source={feed}
          onDrawn={(data, drawnAtMs) => {
            feed.drawn(data, drawnAtMs);
          }}
        />
      </Suspense>
    </section>
  );
}
