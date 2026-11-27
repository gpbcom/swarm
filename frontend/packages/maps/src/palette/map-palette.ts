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

/** Turns any CSS colour into its #rrggbb form, or returns null when it cannot. */
export type ColourResolver = (value: string) => string | null;

const HEX_COLOUR = /^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i;
const SHORT_HEX_COLOUR = /^#([0-9a-f])([0-9a-f])([0-9a-f])$/i;
const OPAQUE = 255;
const BLACK = "#000000";
const WHITE = "#ffffff";

const TOKENS: Record<keyof MapPalette, string> = {
  background: "--color-background",
  surface: "--color-surface",
  border: "--color-border",
  muted: "--color-muted",
  text: "--color-text",
  drone: "--color-entity",
  droneLost: "--color-failure",
};

/**
 * Resolve a CSS colour with a 2D canvas, which writes back every opaque colour as #rrggbb.
 * A value the canvas refuses leaves the previous colour in place, so it is tried over black and over white.
 */
export const resolveWithCanvas: ColourResolver = (value) => {
  const context = document.createElement("canvas").getContext("2d");
  if (!context) {
    return null;
  }
  context.fillStyle = BLACK;
  context.fillStyle = value;
  const overBlack = context.fillStyle;
  context.fillStyle = WHITE;
  context.fillStyle = value;
  const overWhite = context.fillStyle;
  return overBlack === overWhite ? overBlack : null;
};

/** Write a colour as #rrggbb: the long form as it is, the short form expanded, any other form through the resolver. */
function longHex(value: string, resolve: ColourResolver): string | null {
  if (HEX_COLOUR.test(value)) {
    return value;
  }
  const short = SHORT_HEX_COLOUR.exec(value);
  if (short) {
    return `#${short
      .slice(1)
      .map((digit) => digit + digit)
      .join("")}`;
  }
  return resolve(value);
}

function parseToken(name: string, raw: string, resolve: ColourResolver): Rgba {
  const value = raw.trim();
  if (value === "") {
    throw new MapPaletteError(`The token ${name} is not defined.`);
  }
  const match = HEX_COLOUR.exec(longHex(value, resolve) ?? "");
  if (!match) {
    throw new MapPaletteError(`The token ${name} is not an opaque CSS colour: ${value}.`);
  }
  const [red = "0", green = "0", blue = "0"] = match.slice(1);
  return [parseInt(red, 16), parseInt(green, 16), parseInt(blue, 16), OPAQUE];
}

/**
 * Read the map colours from the token CSS variables of an element, as opaque RGBA arrays.
 * The tokens are written #rrggbb, but the production build minifies the stylesheet, which writes each colour in its
 * shortest form (#fff, red): every opaque CSS colour is accepted.
 */
export function readMapPalette(
  element: HTMLElement = document.documentElement,
  resolve: ColourResolver = resolveWithCanvas,
): MapPalette {
  const computed = getComputedStyle(element);
  const read = (key: keyof MapPalette): Rgba =>
    parseToken(TOKENS[key], computed.getPropertyValue(TOKENS[key]), resolve);
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
