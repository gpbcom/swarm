import { afterEach, describe, expect, it } from "vitest";

import { MapPaletteError, readMapPalette } from "../../src/palette/map-palette";

const VARIABLES: Record<string, string> = {
  "--color-background": "#102030",
  "--color-surface": "#ffffff",
  "--color-border": "#0a0b0c",
  "--color-muted": "#808080",
  "--color-text": "#111111",
  "--color-entity": "#00aaff",
  "--color-failure": "#ff0000",
};

function paint(element: HTMLElement, skip?: string, override?: Record<string, string>): void {
  const values = { ...VARIABLES, ...override };
  for (const [name, value] of Object.entries(values)) {
    if (name !== skip) {
      element.style.setProperty(name, value);
    }
  }
}

describe("readMapPalette", () => {
  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("converts each token to an opaque rgba array", () => {
    const element = document.createElement("div");
    document.body.appendChild(element);
    paint(element);
    const palette = readMapPalette(element);
    expect(palette.background).toEqual([16, 32, 48, 255]);
    expect(palette.surface).toEqual([255, 255, 255, 255]);
    expect(palette.border).toEqual([10, 11, 12, 255]);
    expect(palette.muted).toEqual([128, 128, 128, 255]);
    expect(palette.text).toEqual([17, 17, 17, 255]);
    expect(palette.drone).toEqual([0, 170, 255, 255]);
    expect(palette.droneLost).toEqual([255, 0, 0, 255]);
  });

  it.each(Object.keys(VARIABLES))("refuses a palette without %s", (name) => {
    const element = document.createElement("div");
    document.body.appendChild(element);
    paint(element, name);
    expect(() => readMapPalette(element)).toThrow(MapPaletteError);
  });

  it.each(["red", "#fff", "#12345", "rgb(1,2,3)", "#gggggg"])("refuses the malformed value %s", (value) => {
    const element = document.createElement("div");
    document.body.appendChild(element);
    paint(element, undefined, { "--color-text": value });
    expect(() => readMapPalette(element)).toThrow(MapPaletteError);
  });
});
