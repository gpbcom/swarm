import assert from "node:assert/strict";
import { afterEach, beforeEach, describe, it } from "node:test";

import { InMemorySpanExporter, type ReadableSpan } from "@opentelemetry/sdk-trace-base";

import { createSignals, type Signals } from "../src/index.ts";

function firstSpan(exporter: InMemorySpanExporter): ReadableSpan {
  const span = exporter.getFinishedSpans()[0];
  assert.ok(span, "no span was exported");
  return span;
}

const TRACE_ID = "4bf92f3577b34da6a3ce929d0e0e4736";
const SPAN_ID = "00f067aa0ba902b7";
const TRACE_PARENT = `00-${TRACE_ID}-${SPAN_ID}-01`;
const SERVICE_NAME = "ground-control";
const CELL = "cell-eu-1";

interface ParentLink {
  parentSpanId?: string;
  parentSpanContext?: { spanId: string };
}

describe("the browser trace continuation", () => {
  let exporter: InMemorySpanExporter;
  let signals: Signals;

  beforeEach(() => {
    exporter = new InMemorySpanExporter();
    signals = createSignals({ serviceName: SERVICE_NAME, cell: CELL, exporter });
  });

  afterEach(async () => {
    await signals.shutdown();
  });

  it("exports a span with the trace id of the trace parent", async () => {
    signals.continueTrace(TRACE_PARENT, "load", {}, () => 1);
    await signals.flush();
    const spans = exporter.getFinishedSpans();
    assert.equal(spans.length, 1);
    assert.equal(firstSpan(exporter).spanContext().traceId, TRACE_ID);
  });

  it("makes the span a child of the span of the trace parent", async () => {
    signals.continueTrace(TRACE_PARENT, "load", {}, () => 1);
    await signals.flush();
    const span = firstSpan(exporter) as unknown as ParentLink;
    assert.equal(span.parentSpanContext?.spanId ?? span.parentSpanId, SPAN_ID);
  });

  it("returns the result of the work", () => {
    assert.equal(
      signals.continueTrace(TRACE_PARENT, "load", {}, () => "done"),
      "done",
    );
  });

  it("returns the result of the work without a trace parent", () => {
    assert.equal(
      signals.continueTrace(undefined, "load", {}, () => "done"),
      "done",
    );
  });

  it("exports no span without a trace parent", async () => {
    signals.continueTrace(undefined, "load", {}, () => 1);
    signals.continueTrace(null, "load", {}, () => 1);
    signals.continueTrace("not a trace parent", "load", {}, () => 1);
    await signals.flush();
    assert.equal(exporter.getFinishedSpans().length, 0);
  });

  it("puts the service name and the cell in the resource", async () => {
    signals.continueTrace(TRACE_PARENT, "load", {}, () => 1);
    await signals.flush();
    const attributes = firstSpan(exporter).resource.attributes;
    assert.equal(attributes["service.name"], SERVICE_NAME);
    assert.equal(attributes["cell"], CELL);
  });

  it("exports the attributes it is given", async () => {
    signals.continueTrace(TRACE_PARENT, "load", { "swarm.screen": "map" }, () => 1);
    await signals.flush();
    assert.equal(firstSpan(exporter).attributes["swarm.screen"], "map");
  });
});
