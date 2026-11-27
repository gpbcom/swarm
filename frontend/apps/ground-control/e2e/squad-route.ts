export const DRONE_COUNT = 10;
export const SIDE_M = 200;
export const SPEED_M_S = 5;
export const CENTRE_LAT = 48.8566;
export const CENTRE_LON = 2.3522;

const METRES_PER_DEGREE = 111_320;
const E7 = 1e7;
const PERIMETER_M = 4 * SIDE_M;
const SPACING_M = 4;
const HALF_M = SIDE_M / 2;

export interface Position {
  lat_e7: number;
  lon_e7: number;
  heading_deg: number;
}

/** Position of one Drone on the square, `elapsedS` seconds after take-off. */
export function squadPosition(index: number, elapsedS: number): Position {
  const along = (elapsedS * SPEED_M_S + index * SPACING_M) % PERIMETER_M;
  const side = Math.floor(along / SIDE_M);
  const offset = along - side * SIDE_M;
  let eastM = -HALF_M + offset;
  let northM = -HALF_M;
  let heading = 90;
  if (side === 1) {
    eastM = HALF_M;
    northM = -HALF_M + offset;
    heading = 0;
  } else if (side === 2) {
    eastM = HALF_M - offset;
    northM = HALF_M;
    heading = 270;
  } else if (side === 3) {
    eastM = -HALF_M;
    northM = HALF_M - offset;
    heading = 180;
  }
  const latitude = CENTRE_LAT + northM / METRES_PER_DEGREE;
  const longitude = CENTRE_LON + eastM / (METRES_PER_DEGREE * Math.cos((CENTRE_LAT * Math.PI) / 180));
  return { lat_e7: Math.round(latitude * E7), lon_e7: Math.round(longitude * E7), heading_deg: heading };
}
