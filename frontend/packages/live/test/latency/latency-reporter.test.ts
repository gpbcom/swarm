import assert from "node:assert/strict";
import { beforeEach, describe, it } from "node:test";

import { LatencyHistogram } from "../../src/latency/latency-histogram.ts";
import { LatencyReporter } from "../../src/latency/latency-reporter.ts";
import { TELEMETRY_METRICS } from "../../src/latency/otlp-metrics-body.ts";

const URL_TEXT = "http://collector.test/v1/metrics";

class FakeClock {
  callback: (() => void) | null = null;
  intervalMs = 0;
  cleared: number[] = [];

  nowMs(): number {
    return 0;
  }

  setInterval(callback: () => void, ms: number): number {
    this.callback = callback;
    this.intervalMs = ms;
    return 7;
  }

  clearInterval(id: number): void {
    this.cleared.push(id);
    this.callback = null;
  }

  async tick(): Promise<void> {
    this.callback?.();
    await new Promise<void>((resolve) => setImmediate(resolve));
  }
}

function firstPost(posts: { url: string; body: string }[]): { url: string; body: string } {
  const post = posts[0];
  assert.ok(post !== undefined);
  return post;
}

describe("the latency reporter", () => {
  let clock: FakeClock;
  let histogram: LatencyHistogram;
  let posts: { url: string; body: string }[];
  let outcome: "ok" | "refused" | "rejected";

  const post = (url: string, body: string): Promise<{ ok: boolean; status: number }> => {
    posts.push({ url, body });
    if (outcome === "rejected") {
      return Promise.reject(new Error("network down"));
    }
    return Promise.resolve(outcome === "ok" ? { ok: true, status: 200 } : { ok: false, status: 503 });
  };

  const reporter = (): LatencyReporter =>
    new LatencyReporter({
      url: URL_TEXT,
      intervalS: 10,
      missionId: "m1",
      cell: "c1",
      path: "cell",
      histograms: { [TELEMETRY_METRICS.droneToScreen]: histogram },
      post,
      clock,
    });

  beforeEach(() => {
    clock = new FakeClock();
    histogram = new LatencyHistogram();
    posts = [];
    outcome = "ok";
  });

  it("posts a JSON body to the url every interval", async () => {
    const instance = reporter();
    instance.start();
    assert.equal(clock.intervalMs, 10_000);
    histogram.record(30);
    await clock.tick();
    assert.equal(posts.length, 1);
    assert.equal(firstPost(posts).url, URL_TEXT);
    const parsed = JSON.parse(firstPost(posts).body) as { resourceMetrics: unknown[] };
    assert.equal(parsed.resourceMetrics.length, 1);
    histogram.record(60);
    await clock.tick();
    assert.equal(posts.length, 2);
    instance.stop();
  });

  it("posts nothing when no sample was recorded", async () => {
    const instance = reporter();
    instance.start();
    await clock.tick();
    assert.equal(posts.length, 0);
    instance.stop();
  });

  it("keeps running after a refused post", async () => {
    const instance = reporter();
    instance.start();
    histogram.record(30);
    outcome = "refused";
    await clock.tick();
    outcome = "ok";
    await clock.tick();
    assert.equal(posts.length, 2);
    instance.stop();
  });

  it("keeps running after a rejected post", async () => {
    const instance = reporter();
    instance.start();
    histogram.record(30);
    outcome = "rejected";
    await clock.tick();
    outcome = "ok";
    await clock.tick();
    assert.equal(posts.length, 2);
    instance.stop();
  });

  it("clears its interval when stopped", () => {
    const instance = reporter();
    instance.start();
    instance.stop();
    assert.deepEqual(clock.cleared, [7]);
  });

  it("posts at once on flush", async () => {
    const instance = reporter();
    histogram.record(30);
    await instance.flush();
    assert.equal(posts.length, 1);
    assert.ok(!firstPost(posts).body.includes("drone_id"));
  });
});
