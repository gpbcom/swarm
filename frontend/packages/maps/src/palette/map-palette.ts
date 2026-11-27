export type Rgba = [number, number, number, number];

export interface MapPalette {
  background: Rgba;
  surface: Rgba;
  border: Rgba;
  muted: Rgba;
  text: Rgba;
  drone: Rgba;
  droneLost: Rgba;
}

export class MapPaletteError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "MapPaletteError";
  }
}

const HEX_COLOUR = /^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i;
const OPAQUE = 255;

const TOKENS: Record<keyof MapPalette, string> = {
  background: "--color-background",
  surface: "--color-surface",
  border: "--color-border",
  muted: "--color-muted",
  text: "--color-text",
  drone: "--color-entity",
  droneLost: "--color-failure",
};

function parseToken(name: string, raw: string): Rgba {
  const value = raw.trim();
  if (value === "") {
    throw new MapPaletteError(`The token ${name} is not defined.`);
  }
  const match = HEX_COLOUR.exec(value);
  if (!match) {
    throw new MapPaletteError(`The token ${name} is not a #rrggbb colour: ${value}.`);
  }
  const [red = "0", green = "0", blue = "0"] = match.slice(1);
  return [parseInt(red, 16), parseInt(green, 16), parseInt(blue, 16), OPAQUE];
}

/** Read the map colours from the token CSS variables of an element, as opaque RGBA arrays. */
export function readMapPalette(element: HTMLElement = document.documentElement): MapPalette {
  const computed = getComputedStyle(element);
  const read = (key: keyof MapPalette): Rgba => parseToken(TOKENS[key], computed.getPropertyValue(TOKENS[key]));
  return {
    background: read("background"),
    surface: read("surface"),
    border: read("border"),
    muted: read("muted"),
    text: read("text"),
    drone: read("drone"),
    droneLost: read("droneLost"),
  };
}
