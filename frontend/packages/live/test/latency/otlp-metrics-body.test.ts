import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { LATENCY_BOUNDS_MS, LatencyHistogram } from "../../src/latency/latency-histogram.ts";
import { TELEMETRY_METRICS, otlpMetricsBody } from "../../src/latency/otlp-metrics-body.ts";

interface Attribute {
  key: string;
  value: { stringValue?: string };
}

interface Metric {
  name: string;
  unit: string;
  histogram: {
    aggregationTemporality: number;
    dataPoints: {
      count: string | number;
      sum: number;
      min: number;
      max: number;
      bucketCounts: (string | number)[];
      explicitBounds: number[];
      attributes: Attribute[];
    }[];
  };
}

interface Parsed {
  resourceMetrics: {
    resource: { attributes: Attribute[] };
    scopeMetrics: { metrics: Metric[] }[];
  }[];
}

function build(missionId: string | null, cell: string | null, path: "edge" | "cell"): Parsed {
  const drone = new LatencyHistogram();
  drone.record(40);
  drone.record(160);
  const pixels = new LatencyHistogram();
  pixels.record(12);
  const body: string | object = otlpMetricsBody({
    missionId,
    cell,
    path,
    startTimeUnixNano: "1000000000",
    timeUnixNano: "2000000000",
    histograms: { [TELEMETRY_METRICS.droneToScreen]: drone, [TELEMETRY_METRICS.frameToPixels]: pixels },
  });
  return JSON.parse(typeof body === "string" ? body : JSON.stringify(body)) as Parsed;
}

function first<T>(items: readonly T[]): T {
  const item = items[0];
  assert.ok(item !== undefined);
  return item;
}

function attributeValue(attributes: Attribute[], key: string): string | undefined {
  return attributes.find((attribute: Attribute) => attribute.key === key)?.value.stringValue;
}

describe("the OTLP metrics body", () => {
  it("names the two latency metrics", () => {
    assert.equal(TELEMETRY_METRICS.droneToScreen, "swarm.telemetry.drone_to_screen");
    assert.equal(TELEMETRY_METRICS.frameToPixels, "swarm.live.frame_to_pixels");
  });

  it("holds one resource, one scope and one histogram per entry", () => {
    const parsed = build("m1", "c1", "edge");
    assert.equal(parsed.resourceMetrics.length, 1);
    assert.equal(first(parsed.resourceMetrics).scopeMetrics.length, 1);
    const names = first(first(parsed.resourceMetrics).scopeMetrics).metrics.map((metric: Metric) => metric.name);
    assert.deepEqual(names.sort(), [TELEMETRY_METRICS.droneToScreen, TELEMETRY_METRICS.frameToPixels].sort());
  });

  it("carries the resource attributes when they are set", () => {
    const attributes = first(build("m1", "c1", "cell").resourceMetrics).resource.attributes;
    assert.equal(attributeValue(attributes, "service.name"), "ground-control");
    assert.equal(attributeValue(attributes, "mission_id"), "m1");
    assert.equal(attributeValue(attributes, "cell"), "c1");
  });

  it("leaves out mission_id and cell when they are not set", () => {
    const attributes = first(build(null, null, "edge").resourceMetrics).resource.attributes;
    assert.equal(attributeValue(attributes, "service.name"), "ground-control");
    assert.equal(attributeValue(attributes, "mission_id"), undefined);
    assert.equal(attributeValue(attributes, "cell"), undefined);
  });

  it("writes cumulative millisecond histograms with the data point", () => {
    const parsed = build("m1", "c1", "edge");
    const metric = first(first(parsed.resourceMetrics).scopeMetrics).metrics.find(
      (item: Metric) => item.name === TELEMETRY_METRICS.droneToScreen,
    );
    assert.ok(metric);
    assert.equal(metric.unit, "ms");
    assert.equal(metric.histogram.aggregationTemporality, 2);
    assert.equal(metric.histogram.dataPoints.length, 1);
    const point = first(metric.histogram.dataPoints);
    assert.equal(Number(point.count), 2);
    assert.equal(point.sum, 200);
    assert.equal(point.min, 40);
    assert.equal(point.max, 160);
    assert.deepEqual(point.explicitBounds, LATENCY_BOUNDS_MS);
    assert.equal(point.bucketCounts.length, LATENCY_BOUNDS_MS.length + 1);
    assert.equal(
      point.bucketCounts.reduce((total: number, value: string | number) => total + Number(value), 0),
      2,
    );
  });

  it("tags each data point with the path", () => {
    for (const path of ["edge", "cell"] as const) {
      const parsed = build("m1", "c1", path);
      for (const metric of first(first(parsed.resourceMetrics).scopeMetrics).metrics) {
        assert.equal(attributeValue(first(metric.histogram.dataPoints).attributes, "swarm.live.path"), path);
      }
    }
  });

  it("never holds drone_id", () => {
    const text: string = JSON.stringify(build("m1", "c1", "cell"));
    assert.ok(!text.includes("drone_id"));
  });
});
