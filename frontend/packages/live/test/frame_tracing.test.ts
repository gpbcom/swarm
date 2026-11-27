import assert from "node:assert/strict";
import { beforeEach, describe, it } from "node:test";

import { InMemorySpanExporter, type ReadableSpan } from "@opentelemetry/sdk-trace-base";
import { createSignals, type Signals } from "@swarm/observability";

import type { SquadFrame } from "../src/generated/models.ts";
import { traceSquadFrame } from "../src/index.ts";

const TRACE_ID = "4bf92f3577b34da6a3ce929d0e0e4736";
const PARENT_SPAN_ID = "00f067aa0ba902b7";
const TRACE_PARENT = `00-${TRACE_ID}-${PARENT_SPAN_ID}-01`;
const SPAN_NAME = "squad_frame receive";
const MISSION_ID = "0192f0c4-7b2a-7c3e-8a51-2f9d6e4b1c70";
const LAT_E7 = 487_000_123;
const LON_E7 = 23_000_456;

interface ParentLink {
  parentSpanContext?: { spanId: string };
  parentSpanId?: string;
}

function squadFrame(traceParent?: string): SquadFrame {
  const frame = {
    mission_id: MISSION_ID,
    t_us: 1_700_000_000_000_000,
    frames: [
      {
        altitude_m: 40,
        battery_pct: 90,
        drone_id: "0192f0c4-7b2a-7c3e-8a51-2f9d6e4b1c71",
        heading_deg: 10,
        lat_e7: LAT_E7,
        link_quality_pct: 95,
        lon_e7: LON_E7,
        mission_id: MISSION_ID,
        seq: 1,
        speed_m_s: 5,
        state: "flying",
        t_us: 1_700_000_000_000_000,
      },
    ],
  };
  if (traceParent === undefined) {
    return frame as unknown as SquadFrame;
  }
  return { ...frame, trace_parent: traceParent } as unknown as SquadFrame;
}

function parentSpanIdOf(span: ReadableSpan): string | undefined {
  const link = span as unknown as ParentLink;
  return link.parentSpanContext?.spanId ?? link.parentSpanId;
}

describe("the browser span of a squad frame", () => {
  let exporter: InMemorySpanExporter;
  let signals: Signals;

  beforeEach(() => {
    exporter = new InMemorySpanExporter();
    signals = createSignals({ serviceName: "ground-control", cell: "test-cell", exporter });
  });

  it("returns the result of the work", async () => {
    const result: number = traceSquadFrame(signals, squadFrame(TRACE_PARENT), () => 42);
    await signals.flush();
    assert.equal(result, 42);
  });

  it("opens a span named after the receive of a squad frame", async () => {
    traceSquadFrame(signals, squadFrame(TRACE_PARENT), () => undefined);
    await signals.flush();
    const names: string[] = exporter.getFinishedSpans().map((span) => span.name);
    assert.deepEqual(names, [SPAN_NAME]);
  });

  it("keeps the trace and the parent span of the frame", async () => {
    traceSquadFrame(signals, squadFrame(TRACE_PARENT), () => undefined);
    await signals.flush();
    const span = exporter.getFinishedSpans()[0];
    assert.ok(span);
    assert.equal(span.spanContext().traceId, TRACE_ID);
    assert.equal(parentSpanIdOf(span), PARENT_SPAN_ID);
  });

  it("sets the mission_id attribute", async () => {
    traceSquadFrame(signals, squadFrame(TRACE_PARENT), () => undefined);
    await signals.flush();
    const span = exporter.getFinishedSpans()[0];
    assert.ok(span);
    assert.equal(span.attributes["mission_id"], MISSION_ID);
  });

  it("runs the work inside the span", async () => {
    let finishedDuringWork = -1;
    traceSquadFrame(signals, squadFrame(TRACE_PARENT), () => {
      finishedDuringWork = exporter.getFinishedSpans().length;
    });
    await signals.flush();
    assert.equal(finishedDuringWork, 0);
    assert.equal(exporter.getFinishedSpans().length, 1);
  });

  it("exports no Drone position", async () => {
    traceSquadFrame(signals, squadFrame(TRACE_PARENT), () => undefined);
    await signals.flush();
    const span = exporter.getFinishedSpans()[0];
    assert.ok(span);
    const text: string = JSON.stringify(span.attributes);
    assert.ok(!text.includes(String(LAT_E7)));
    assert.ok(!text.includes(String(LON_E7)));
    assert.ok(!/lat|lon|altitude|position/i.test(text));
  });

  it("runs the work and exports no span without a trace_parent", async () => {
    const result: number = traceSquadFrame(signals, squadFrame(), () => 7);
    await signals.flush();
    assert.equal(result, 7);
    assert.equal(exporter.getFinishedSpans().length, 0);
  });

  it("runs the work and exports no span without signals", async () => {
    const result: number = traceSquadFrame(undefined, squadFrame(TRACE_PARENT), () => 9);
    await signals.flush();
    assert.equal(result, 9);
    assert.equal(exporter.getFinishedSpans().length, 0);
  });
});
