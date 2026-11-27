import { describe, expect, it } from "vitest";

import { buildBaseStyle } from "../../src/style/base-style";
import type { MapPalette, Rgba } from "../../src/palette/map-palette";

const COLOURS: MapPalette = {
  background: [1, 2, 3, 255],
  surface: [4, 5, 6, 255],
  border: [7, 8, 9, 255],
  muted: [10, 11, 12, 255],
  text: [13, 14, 15, 255],
  drone: [16, 17, 18, 255],
  droneLost: [19, 20, 21, 255],
};

const TILES_URL = "https://tiles.example.test/basemap.pmtiles";

interface LooseLayer {
  id: string;
  type: string;
  source?: string;
  "source-layer"?: string;
  paint?: Record<string, unknown>;
}

function build(palette: MapPalette = COLOURS): ReturnType<typeof buildBaseStyle> {
  return buildBaseStyle({ tilesUrl: TILES_URL, palette });
}

function layers(palette: MapPalette = COLOURS): LooseLayer[] {
  return build(palette).layers;
}

function hex(rgba: Rgba): string {
  return `#${rgba
    .slice(0, 3)
    .map((part) => part.toString(16).padStart(2, "0"))
    .join("")}`;
}

function allowedColours(): string[] {
  const forms: string[] = [];
  const swatches: Rgba[] = [
    COLOURS.background,
    COLOURS.surface,
    COLOURS.border,
    COLOURS.muted,
    COLOURS.text,
    COLOURS.drone,
    COLOURS.droneLost,
  ];
  for (const rgba of swatches) {
    const channels = rgba.slice(0, 3);
    forms.push(
      hex(rgba),
      `rgb(${channels.join(", ")})`,
      `rgb(${channels.join(",")})`,
      `rgba(${channels.join(", ")}, 1)`,
    );
  }
  return forms;
}

describe("buildBaseStyle", () => {
  it("is a version 8 style", () => {
    expect(build().version).toBe(8);
  });

  it("has one vector source named basemap on the pmtiles protocol", () => {
    const style = build();
    expect(Object.keys(style.sources)).toEqual(["basemap"]);
    const source = style.sources["basemap"] as { type: string; url: string; attribution?: string };
    expect(source.type).toBe("vector");
    expect(source.url).toBe(`pmtiles://${TILES_URL}`);
    expect(source.attribution).toContain("© OpenStreetMap contributors");
  });

  it("starts with a background layer in the palette background", () => {
    const [first] = layers();
    expect(first?.type).toBe("background");
    expect(allowedColours()).toContain(first?.paint?.["background-color"]);
  });

  it.each(["earth", "water", "landuse", "roads", "buildings"])("draws the %s source layer", (name) => {
    const drawn = layers().filter((layer) => layer["source-layer"] === name);
    expect(drawn.length).toBeGreaterThan(0);
    for (const layer of drawn) {
      expect(["fill", "line"]).toContain(layer.type);
      expect(layer.source).toBe("basemap");
    }
  });

  it("colours every layer from the palette only", () => {
    const allowed = allowedColours();
    for (const layer of layers()) {
      for (const [key, value] of Object.entries(layer.paint ?? {})) {
        if (key.endsWith("-color")) {
          expect(allowed).toContain(value);
        }
      }
    }
  });

  it("has no glyphs, no sprite and no symbol layer", () => {
    const style = build();
    expect(style.glyphs).toBeUndefined();
    expect(style.sprite).toBeUndefined();
    expect(layers().some((layer) => layer.type === "symbol")).toBe(false);
  });

  it("follows the palette it is given", () => {
    const other: MapPalette = { ...COLOURS, background: [200, 100, 50, 255] };
    const [changed] = layers(other);
    const [original] = layers();
    expect(changed?.paint?.["background-color"]).not.toBe(original?.paint?.["background-color"]);
  });
});
