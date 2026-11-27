import assert from "node:assert/strict";
import { afterEach, beforeEach, describe, it } from "node:test";

import { InMemorySpanExporter, type ReadableSpan } from "@opentelemetry/sdk-trace-base";

import { createSignals, type Signals } from "../src/index.ts";

function firstSpan(exporter: InMemorySpanExporter): ReadableSpan {
  const span = exporter.getFinishedSpans()[0];
  assert.ok(span, "no span was exported");
  return span;
}

const TRACE_PARENT = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01";
const SENSITIVE_KEYS: string[] = [
  "authorization",
  "http.request.header.Authorization",
  "token",
  "access_token",
  "password",
  "db.password",
  "secret",
  "client_secret",
  "cookie",
  "http.request.header.cookie",
  "email",
  "user.email",
];

describe("the redaction of signals", () => {
  let exporter: InMemorySpanExporter;
  let signals: Signals;

  beforeEach(() => {
    exporter = new InMemorySpanExporter();
    signals = createSignals({ serviceName: "ground-control", cell: "cell-eu-1", exporter });
  });

  afterEach(async () => {
    await signals.shutdown();
  });

  for (const key of SENSITIVE_KEYS) {
    it(`does not export the attribute ${key}`, async () => {
      signals.continueTrace(TRACE_PARENT, "load", { [key]: "private", kept: "public" }, () => 1);
      await signals.flush();
      const attributes = firstSpan(exporter).attributes;
      assert.equal(attributes[key], undefined);
      assert.equal(attributes["kept"], "public");
    });
  }

  it("does not export the value of a sensitive attribute under any key", async () => {
    const attributes: Record<string, string> = {};
    for (const key of SENSITIVE_KEYS) {
      attributes[key] = "private-value";
    }
    signals.continueTrace(TRACE_PARENT, "load", attributes, () => 1);
    await signals.flush();
    const exported = firstSpan(exporter).attributes;
    assert.ok(!Object.values(exported).includes("private-value"));
  });
});
