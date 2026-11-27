import { Protocol } from "pmtiles";

export interface ProtocolTarget {
  addProtocol(name: string, loader: Protocol["tile"]): void;
}

const PROTOCOL_NAME = "pmtiles";

let registered = false;

/** Register the pmtiles protocol on MapLibre once, however many times it is called. */
export function registerPmtilesProtocol(target: ProtocolTarget): void {
  if (registered) {
    return;
  }
  const protocol = new Protocol();
  target.addProtocol(PROTOCOL_NAME, protocol.tile);
  registered = true;
}
