import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { LATENCY_BOUNDS_MS, LatencyHistogram } from "../../src/latency/latency-histogram.ts";

describe("the latency histogram", () => {
  it("has the bounds of the Telemetry latency budgets", () => {
    assert.deepEqual(LATENCY_BOUNDS_MS, [10, 25, 50, 75, 100, 150, 200, 300, 400, 600, 800, 1000, 2000]);
  });

  it("starts empty with one more bucket than bounds", () => {
    const histogram = new LatencyHistogram();
    assert.equal(histogram.count, 0);
    assert.equal(histogram.sum, 0);
    assert.equal(histogram.skipped, 0);
    const counts: number[] = histogram.bucketCounts();
    assert.equal(counts.length, LATENCY_BOUNDS_MS.length + 1);
    assert.ok(counts.every((value: number) => value === 0));
  });

  it("puts a value equal to a bound in that bound's bucket", () => {
    const histogram = new LatencyHistogram();
    histogram.record(10);
    histogram.record(150);
    const counts: number[] = histogram.bucketCounts();
    assert.equal(counts[0], 1);
    assert.equal(counts[LATENCY_BOUNDS_MS.indexOf(150)], 1);
  });

  it("puts a value between two bounds in the upper bound's bucket", () => {
    const histogram = new LatencyHistogram();
    histogram.record(11);
    histogram.record(151);
    const counts: number[] = histogram.bucketCounts();
    assert.equal(counts[1], 1);
    assert.equal(counts[LATENCY_BOUNDS_MS.indexOf(200)], 1);
  });

  it("puts a value above the last bound in the overflow bucket", () => {
    const histogram = new LatencyHistogram();
    histogram.record(2001);
    const counts: number[] = histogram.bucketCounts();
    assert.equal(counts[counts.length - 1], 1);
  });

  it("keeps count, sum, min and max", () => {
    const histogram = new LatencyHistogram();
    for (const value of [40, 5, 120]) {
      histogram.record(value);
    }
    assert.equal(histogram.count, 3);
    assert.equal(histogram.sum, 165);
    assert.equal(histogram.min, 5);
    assert.equal(histogram.max, 120);
    assert.equal(
      histogram.bucketCounts().reduce((total: number, value: number) => total + value, 0),
      3,
    );
  });

  it("skips negative and non-finite values", () => {
    const histogram = new LatencyHistogram();
    for (const value of [-1, Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY]) {
      histogram.record(value);
    }
    assert.equal(histogram.count, 0);
    assert.equal(histogram.skipped, 4);
    assert.equal(histogram.sum, 0);
  });

  it("records zero", () => {
    const histogram = new LatencyHistogram();
    histogram.record(0);
    assert.equal(histogram.count, 1);
    assert.equal(histogram.skipped, 0);
    assert.equal(histogram.bucketCounts()[0], 1);
  });

  it("accepts custom bounds", () => {
    const histogram = new LatencyHistogram([5, 10]);
    histogram.record(5);
    histogram.record(7);
    histogram.record(99);
    assert.deepEqual(histogram.bucketCounts(), [1, 1, 1]);
  });
});
