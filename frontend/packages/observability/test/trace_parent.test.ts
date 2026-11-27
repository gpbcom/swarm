import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { parseTraceParent } from "../src/index.ts";

const TRACE_ID = "4bf92f3577b34da6a3ce929d0e0e4736";
const SPAN_ID = "00f067aa0ba902b7";
const VALID = `00-${TRACE_ID}-${SPAN_ID}-01`;

describe("the W3C trace parent parser", () => {
  it("reads the trace id and the span id of a valid value", () => {
    const context = parseTraceParent(VALID);
    assert.equal(context?.traceId, TRACE_ID);
    assert.equal(context?.spanId, SPAN_ID);
  });

  it("marks the context as remote", () => {
    assert.equal(parseTraceParent(VALID)?.isRemote, true);
  });

  it("keeps the sampled flag", () => {
    assert.equal(parseTraceParent(VALID)?.traceFlags, 1);
    assert.equal(parseTraceParent(`00-${TRACE_ID}-${SPAN_ID}-00`)?.traceFlags, 0);
  });

  const refused: Array<[string, string | null | undefined]> = [
    ["a missing value", undefined],
    ["a null value", null],
    ["an empty value", ""],
    ["a text that is not a trace parent", "hello"],
    ["an unknown version", `01-${TRACE_ID}-${SPAN_ID}-01`],
    ["upper-case hex", `00-${TRACE_ID.toUpperCase()}-${SPAN_ID}-01`],
    ["an all-zero trace id", `00-${"0".repeat(32)}-${SPAN_ID}-01`],
    ["an all-zero span id", `00-${TRACE_ID}-${"0".repeat(16)}-01`],
    ["a short trace id", `00-${TRACE_ID.slice(1)}-${SPAN_ID}-01`],
    ["a short span id", `00-${TRACE_ID}-${SPAN_ID.slice(1)}-01`],
    ["a trace id that is not hex", `00-${"g".repeat(32)}-${SPAN_ID}-01`],
    ["a missing flags field", `00-${TRACE_ID}-${SPAN_ID}`],
  ];

  for (const [name, value] of refused) {
    it(`refuses ${name}`, () => {
      assert.equal(parseTraceParent(value), undefined);
    });
  }
});
