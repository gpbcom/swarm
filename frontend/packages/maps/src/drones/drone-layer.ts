import { ScatterplotLayer } from "@deck.gl/layers";

import type { MapPalette } from "../palette/map-palette";

/** The state code of a Drone whose link is lost. */
export const LOST_STATE = 5;

/** The Squad as binary buffers, updated in place by the live data worker. */
export interface DroneLayerData {
  version: number;
  count: number;
  /** Longitude, latitude, altitude of each Drone, three values per Drone. */
  positions: Float64Array;
  /** One state code per Drone. */
  states: Uint8Array;
}

const COLOUR_SIZE = 4;
const RADIUS_PX = 7;

/** Colour buffer kept between calls, reallocated only when the count changes. */
class ColourBuffer {
  current: Uint8Array = new Uint8Array(0);

  fill(data: DroneLayerData, palette: MapPalette): Uint8Array {
    if (this.current.length !== data.count * COLOUR_SIZE) {
      this.current = new Uint8Array(data.count * COLOUR_SIZE);
    }
    const buffer = this.current;
    for (let index = 0; index < data.count; index += 1) {
      const colour = data.states[index] === LOST_STATE ? palette.droneLost : palette.drone;
      buffer.set(colour, index * COLOUR_SIZE);
    }
    return buffer;
  }
}

const COLOURS = new ColourBuffer();

/** Build the GPU layer of the Drones, from binary attributes only. */
export function buildDroneLayer(data: DroneLayerData, palette: MapPalette): ScatterplotLayer {
  const colours = COLOURS.fill(data, palette);
  return new ScatterplotLayer({
    id: "drones",
    data: {
      length: data.count,
      attributes: {
        getPosition: { value: data.positions, size: 3 },
        getFillColor: { value: colours, size: COLOUR_SIZE, normalized: true },
      },
    },
    getPosition: [0, 0, 0],
    getFillColor: [0, 0, 0, 255],
    radiusUnits: "pixels",
    getRadius: RADIUS_PX,
    radiusMinPixels: RADIUS_PX,
    pickable: true,
    updateTriggers: { getPosition: [data.version], getFillColor: [data.version] },
  });
}
