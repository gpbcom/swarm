import { describe, expect, it } from "vitest";

import { LOST_STATE, buildDroneLayer } from "../../src/drones/drone-layer";
import type { DroneLayerData } from "../../src/drones/drone-layer";
import type { MapPalette } from "../../src/palette/map-palette";

const PALETTE: MapPalette = {
  background: [0, 0, 0, 255],
  surface: [1, 1, 1, 255],
  border: [2, 2, 2, 255],
  muted: [3, 3, 3, 255],
  text: [4, 4, 4, 255],
  drone: [10, 20, 30, 255],
  droneLost: [200, 100, 50, 255],
};

interface Attribute {
  value: Float64Array | Uint8Array;
  size: number;
  normalized?: boolean;
}

interface LayerData {
  length: number;
  attributes: { getPosition: Attribute; getFillColor: Attribute };
}

function sample(version: number): DroneLayerData {
  return {
    version,
    count: 3,
    positions: new Float64Array([2, 48, 10, 3, 49, 20, 4, 50, 30]),
    states: new Uint8Array([0, LOST_STATE, 2]),
  };
}

function props(version: number): Record<string, unknown> {
  return buildDroneLayer(sample(version), PALETTE).props as Record<string, unknown>;
}

describe("buildDroneLayer", () => {
  it("is the drones layer", () => {
    expect(buildDroneLayer(sample(1), PALETTE).id).toBe("drones");
  });

  it("marks the lost state as 5", () => {
    expect(LOST_STATE).toBe(5);
  });

  it("hands the positions over as a binary attribute without copying", () => {
    const data = sample(1);
    const layerData = (buildDroneLayer(data, PALETTE).props as unknown as { data: LayerData }).data;
    expect(layerData.length).toBe(3);
    expect(layerData.attributes.getPosition.value).toBe(data.positions);
    expect(layerData.attributes.getPosition.size).toBe(3);
  });

  it("builds one normalised rgba colour per Drone, lost ones apart", () => {
    const colours = (props(1) as unknown as { data: LayerData }).data.attributes.getFillColor;
    expect(colours.size).toBe(4);
    expect(colours.normalized).toBe(true);
    expect(colours.value).toBeInstanceOf(Uint8Array);
    expect(colours.value.length).toBe(12);
    const at = (index: number): number[] => Array.from(colours.value.slice(index * 4, index * 4 + 4));
    expect(at(0)).toEqual(PALETTE.drone);
    expect(at(1)).toEqual(PALETTE.droneLost);
    expect(at(2)).toEqual(PALETTE.drone);
  });

  it("uses no per-object accessor function", () => {
    const p = props(1);
    expect(typeof p["getPosition"]).not.toBe("function");
    expect(typeof p["getFillColor"]).not.toBe("function");
  });

  it("keys its update triggers on the data version", () => {
    const first = JSON.stringify(props(1)["updateTriggers"]);
    const second = JSON.stringify(props(2)["updateTriggers"]);
    expect(first).toContain("1");
    expect(first).not.toBe(second);
  });
});
