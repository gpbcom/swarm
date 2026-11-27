import { describe, expect, it } from "vitest";

import { squadBounds } from "../../src/drones/fit-squad";
import type { DroneLayerData } from "../../src/drones/drone-layer";

function data(count: number, positions: number[]): DroneLayerData {
  return { version: 1, count, positions: new Float64Array(positions), states: new Uint8Array(count) };
}

describe("squadBounds", () => {
  it("is null for an empty squad", () => {
    expect(squadBounds(data(0, []))).toBeNull();
  });

  it("is the point itself for one Drone", () => {
    expect(squadBounds(data(1, [2.5, 48.5, 100]))).toEqual([
      [2.5, 48.5],
      [2.5, 48.5],
    ]);
  });

  it("is the south west and north east corners of several Drones", () => {
    expect(squadBounds(data(3, [2, 48, 10, -1, 50, 20, 4, 47, 30]))).toEqual([
      [-1, 47],
      [4, 50],
    ]);
  });

  it("reads only count Drones", () => {
    expect(squadBounds(data(1, [2, 48, 10, 90, 80, 20]))).toEqual([
      [2, 48],
      [2, 48],
    ]);
  });
});
