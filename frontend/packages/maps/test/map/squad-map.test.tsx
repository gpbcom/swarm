import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Mock } from "vitest";

import type { DroneLayerData } from "../../src/drones/drone-layer";
import type { MapPalette } from "../../src/palette/map-palette";
import { SquadMap } from "../../src/map/SquadMap";

const PALETTE: MapPalette = {
  background: [0, 0, 0, 255],
  surface: [1, 1, 1, 255],
  border: [2, 2, 2, 255],
  muted: [3, 3, 3, 255],
  text: [4, 4, 4, 255],
  drone: [10, 20, 30, 255],
  droneLost: [200, 100, 50, 255],
};

const TILES_URL = "https://tiles.example.test/basemap.pmtiles";

class FakeHandle {
  setLayers = vi.fn<(layers: unknown[]) => void>();
  fitBounds = vi.fn<(bounds: unknown) => void>();
  remove = vi.fn<() => void>();
  afterRender: (() => void)[] = [];
  onAfterRender(callback: () => void): void {
    this.afterRender.push(callback);
  }
}

class FakeSource {
  data: DroneLayerData | null = null;
  listeners = new Set<() => void>();
  current(): DroneLayerData | null {
    return this.data;
  }
  subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }
  publish(data: DroneLayerData | null): void {
    this.data = data;
    for (const listener of [...this.listeners]) {
      listener();
    }
  }
}

function sample(version: number): DroneLayerData {
  return {
    version,
    count: 2,
    positions: new Float64Array([2, 48, 10, 3, 49, 20]),
    states: new Uint8Array([0, 0]),
  };
}

let frames: (() => void)[] = [];

function flushFrames(): void {
  const pending = frames;
  frames = [];
  act(() => {
    for (const callback of pending) {
      callback();
    }
  });
}

describe("SquadMap", () => {
  let handle: FakeHandle;
  let source: FakeSource;
  let createMap: Mock<() => FakeHandle>;

  beforeEach(() => {
    frames = [];
    vi.stubGlobal("requestAnimationFrame", (callback: () => void) => {
      frames.push(callback);
      return frames.length;
    });
    vi.stubGlobal("cancelAnimationFrame", () => undefined);
    handle = new FakeHandle();
    source = new FakeSource();
    createMap = vi.fn(() => handle);
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  function mount(onDrawn?: (data: DroneLayerData, drawnAtMs: number) => void): ReturnType<typeof render> {
    return render(
      <SquadMap
        tilesUrl={TILES_URL}
        palette={PALETTE}
        label="Squad map"
        source={source}
        onDrawn={onDrawn}
        createMap={createMap}
      />,
    );
  }

  it("renders a labelled map region", () => {
    mount();
    expect(screen.getByRole("region", { name: "Squad map" }).className).toBe("map");
  });

  it("creates one map", () => {
    mount();
    expect(createMap).toHaveBeenCalledTimes(1);
  });

  it("sets the Drone layer at most once per animation frame", () => {
    mount();
    act(() => {
      source.publish(sample(1));
      source.publish(sample(2));
      source.publish(sample(3));
    });
    flushFrames();
    expect(handle.setLayers).toHaveBeenCalledTimes(1);
    const layers = handle.setLayers.mock.calls.flatMap((call) => call[0]) as { id: string }[];
    expect(layers.map((layer) => layer.id)).toContain("drones");
  });

  it("fits the bounds once, on the first non-empty data", () => {
    mount();
    act(() => {
      source.publish({ ...sample(1), count: 0 });
    });
    flushFrames();
    expect(handle.fitBounds).not.toHaveBeenCalled();
    act(() => {
      source.publish(sample(2));
    });
    flushFrames();
    act(() => {
      source.publish(sample(3));
    });
    flushFrames();
    expect(handle.fitBounds).toHaveBeenCalledTimes(1);
  });

  it("reports the data drawn once the map has rendered it", () => {
    const onDrawn = vi.fn();
    mount(onDrawn);
    const data = sample(1);
    act(() => {
      source.publish(data);
    });
    flushFrames();
    expect(onDrawn).not.toHaveBeenCalled();
    act(() => {
      for (const callback of handle.afterRender) {
        callback();
      }
    });
    expect(onDrawn).toHaveBeenCalledTimes(1);
    const [drawn, drawnAtMs] = onDrawn.mock.calls.flat() as [DroneLayerData, number];
    expect(drawn).toBe(data);
    expect(typeof drawnAtMs).toBe("number");
  });

  it("removes the map and unsubscribes when it unmounts", () => {
    const { unmount } = mount();
    expect(source.listeners.size).toBe(1);
    unmount();
    expect(handle.remove).toHaveBeenCalledTimes(1);
    expect(source.listeners.size).toBe(0);
  });
});
