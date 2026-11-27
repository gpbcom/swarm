import { MapboxOverlay } from "@deck.gl/mapbox";
import * as maplibregl from "maplibre-gl";
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore The stylesheet has no type declaration unless the host adds vite/client, and the bundler resolves it.
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef, useState } from "react";
import type { ReactElement } from "react";

import { buildDroneLayer } from "../drones/drone-layer";
import type { DroneLayerData } from "../drones/drone-layer";
import { squadBounds } from "../drones/fit-squad";
import type { SquadBounds } from "../drones/fit-squad";
import { readMapPalette } from "../palette/map-palette";
import type { MapPalette } from "../palette/map-palette";
import { registerPmtilesProtocol } from "../style/pmtiles-protocol";
import { buildBaseStyle } from "../style/base-style";

/** The live source of the Squad: the current buffers and a way to be told of a change. */
export interface SquadSource<T extends DroneLayerData> {
  current(): T | null;
  subscribe(listener: () => void): () => void;
}

/** What SquadMap needs from a map and its overlay. */
export interface MapHandle {
  setLayers(layers: unknown[]): void;
  fitBounds(bounds: SquadBounds): void;
  onAfterRender(callback: () => void): void;
  remove(): void;
}

export interface CreateMapOptions {
  container: HTMLElement;
  tilesUrl: string;
  palette: MapPalette;
}

export interface SquadMapProps<T extends DroneLayerData> {
  tilesUrl: string;
  /** The map colours; read from the tokens of the container, and again when the colour scheme changes, when absent. */
  palette?: MapPalette | undefined;
  label: string;
  source: SquadSource<T>;
  /** Called once per drawn version, with the time of the draw in milliseconds. */
  onDrawn?: ((data: T, drawnAtMs: number) => void) | undefined;
  createMap?: ((options: CreateMapOptions) => MapHandle) | undefined;
}

const START_CENTER: [number, number] = [0, 20];
const START_ZOOM = 1;
const FIT_PADDING_PX = 64;
const FIT_MAX_ZOOM = 16;
const SCHEME_QUERY = "(prefers-color-scheme: dark)";

/** The MapLibre map with the deck.gl overlay of the Drones, created over a container. */
export function createMapLibreHandle(options: CreateMapOptions): MapHandle {
  registerPmtilesProtocol(maplibregl);
  const map = new maplibregl.Map({
    container: options.container,
    style: buildBaseStyle({ tilesUrl: options.tilesUrl, palette: options.palette }),
    center: START_CENTER,
    zoom: START_ZOOM,
  });
  const overlay = new MapboxOverlay({ interleaved: true, layers: [] });
  map.addControl(overlay);
  return {
    setLayers: (layers) => {
      overlay.setProps({ layers: layers as never });
    },
    fitBounds: (bounds) => {
      map.fitBounds(bounds, { padding: FIT_PADDING_PX, maxZoom: FIT_MAX_ZOOM, duration: 0 });
    },
    onAfterRender: (callback) => {
      overlay.setProps({ onAfterRender: callback });
    },
    remove: () => {
      map.removeControl(overlay);
      map.remove();
    },
  };
}

/** The map of the Squad, drawn at the display rate from binary buffers, with React only around it. */
export function SquadMap<T extends DroneLayerData>(props: SquadMapProps<T>): ReactElement {
  const { tilesUrl, palette, label, source, createMap = createMapLibreHandle } = props;
  const containerRef = useRef<HTMLDivElement>(null);
  const onDrawnRef = useRef(props.onDrawn);
  onDrawnRef.current = props.onDrawn;
  const [scheme, setScheme] = useState(0);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return undefined;
    }
    const colours = palette ?? readMapPalette(container);
    const handle = createMap({ container, tilesUrl, palette: colours });
    let fitted = false;
    let frame: number | undefined;
    let pending: T | null = null;
    let drawnVersion: number | null = null;

    const draw = (): void => {
      frame = undefined;
      const data = source.current();
      if (!data) {
        return;
      }
      pending = data;
      handle.setLayers([buildDroneLayer(data, colours)]);
      if (!fitted) {
        const bounds = squadBounds(data);
        if (bounds) {
          handle.fitBounds(bounds);
          fitted = true;
        }
      }
    };
    const schedule = (): void => {
      frame ??= requestAnimationFrame(draw);
    };

    handle.onAfterRender(() => {
      if (pending && pending.version !== drawnVersion) {
        drawnVersion = pending.version;
        onDrawnRef.current?.(pending, Date.now());
      }
    });
    const unsubscribe = source.subscribe(schedule);
    schedule();

    let media: MediaQueryList | null = null;
    const onScheme = (): void => {
      setScheme((value) => value + 1);
    };
    if (!palette && typeof window.matchMedia === "function") {
      media = window.matchMedia(SCHEME_QUERY);
      media.addEventListener("change", onScheme);
    }

    return () => {
      unsubscribe();
      media?.removeEventListener("change", onScheme);
      if (frame !== undefined) {
        cancelAnimationFrame(frame);
      }
      handle.remove();
    };
  }, [tilesUrl, palette, source, createMap, scheme]);

  return <div ref={containerRef} className="map" role="region" aria-label={label} />;
}
