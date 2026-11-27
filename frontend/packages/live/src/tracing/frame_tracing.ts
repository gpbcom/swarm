import type { Signals } from "@swarm/observability";

import type { SquadFrame } from "../generated/models.ts";

const SPAN_NAME = "squad_frame receive";
const MISSION_ID_KEY = "mission_id";

/** Run `work` inside the browser span that continues the trace a SquadFrame carries; without signals, just run it. */
export function traceSquadFrame<T>(signals: Signals | undefined, frame: SquadFrame, work: () => T): T {
  if (signals === undefined) {
    return work();
  }
  return signals.continueTrace(frame.trace_parent, SPAN_NAME, { [MISSION_ID_KEY]: frame.mission_id }, work);
}
