import type { LayerSpecification, StyleSpecification } from "maplibre-gl";

import type { MapPalette, Rgba } from "../palette/map-palette";

export interface BaseStyleOptions {
  tilesUrl: string;
  palette: MapPalette;
}

const SOURCE = "basemap";
const ATTRIBUTION = "© OpenStreetMap contributors";

function hex(colour: Rgba): string {
  return `#${colour
    .slice(0, 3)
    .map((part) => part.toString(16).padStart(2, "0"))
    .join("")}`;
}

/** Build the vector base style from PMTiles, coloured only from the palette, with no glyphs or sprite. */
export function buildBaseStyle(options: BaseStyleOptions): StyleSpecification {
  const { palette } = options;
  const layers: LayerSpecification[] = [
    { id: "background", type: "background", paint: { "background-color": hex(palette.background) } },
    {
      id: "earth",
      type: "fill",
      source: SOURCE,
      "source-layer": "earth",
      paint: { "fill-color": hex(palette.background) },
    },
    {
      id: "landuse",
      type: "fill",
      source: SOURCE,
      "source-layer": "landuse",
      paint: { "fill-color": hex(palette.surface) },
    },
    {
      id: "water",
      type: "fill",
      source: SOURCE,
      "source-layer": "water",
      paint: { "fill-color": hex(palette.border) },
    },
    {
      id: "buildings",
      type: "fill",
      source: SOURCE,
      "source-layer": "buildings",
      paint: { "fill-color": hex(palette.muted), "fill-opacity": 0.5 },
    },
    {
      id: "roads",
      type: "line",
      source: SOURCE,
      "source-layer": "roads",
      paint: { "line-color": hex(palette.text), "line-opacity": 0.4, "line-width": 1 },
    },
  ];
  return {
    version: 8,
    sources: {
      [SOURCE]: { type: "vector", url: `pmtiles://${options.tilesUrl}`, attribution: ATTRIBUTION },
    },
    layers,
  };
}
