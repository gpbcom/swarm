import type { DroneLayerData } from "./drone-layer";

export type SquadBounds = [[number, number], [number, number]];

/** The south west and north east corners around the Squad, or null when it is empty. */
export function squadBounds(data: DroneLayerData): SquadBounds | null {
  if (data.count === 0) {
    return null;
  }
  let west = Infinity;
  let south = Infinity;
  let east = -Infinity;
  let north = -Infinity;
  for (let index = 0; index < data.count; index += 1) {
    const lon = data.positions[index * 3] ?? 0;
    const lat = data.positions[index * 3 + 1] ?? 0;
    west = Math.min(west, lon);
    east = Math.max(east, lon);
    south = Math.min(south, lat);
    north = Math.max(north, lat);
  }
  return [
    [west, south],
    [east, north],
  ];
}
