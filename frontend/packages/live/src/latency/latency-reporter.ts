import type { LatencyHistogram } from "./latency-histogram.ts";
import { type LivePath, otlpMetricsBody } from "./otlp-metrics-body.ts";

export interface PostResult {
  ok: boolean;
  status: number;
}

export type PostFunction = (url: string, body: string) => Promise<PostResult>;

export interface ReporterClock {
  nowMs(): number;
  setInterval(callback: () => void, ms: number): number;
  clearInterval(id: number): void;
}

export interface LatencyReporterOptions {
  url: string;
  intervalS: number;
  missionId: string | null;
  cell: string | null;
  path: LivePath;
  histograms: Record<string, LatencyHistogram>;
  post?: PostFunction;
  clock?: ReporterClock;
}

const defaultPost: PostFunction = async (url: string, body: string): Promise<PostResult> => {
  const response = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body });
  return { ok: response.ok, status: response.status };
};

const defaultClock: ReporterClock = {
  nowMs: () => Date.now(),
  setInterval: (callback: () => void, ms: number): number => Number(setInterval(callback, ms)),
  clearInterval: (id: number): void => {
    clearInterval(id);
  },
};

function nanos(ms: number): string {
  return `${String(Math.round(ms))}000000`;
}

/** Posts the latency histograms to an OTLP/HTTP collector every interval, when new samples came. */
export class LatencyReporter {
  private readonly options: LatencyReporterOptions;
  private readonly post: PostFunction;
  private readonly clock: ReporterClock;
  private readonly startMs: number;
  private timer: number | null = null;
  private postedCount = 0;
  private warned = false;

  constructor(options: LatencyReporterOptions) {
    this.options = options;
    this.post = options.post ?? defaultPost;
    this.clock = options.clock ?? defaultClock;
    this.startMs = this.clock.nowMs();
  }

  start(): void {
    if (this.timer !== null) {
      return;
    }
    this.timer = this.clock.setInterval(() => {
      void this.flush();
    }, this.options.intervalS * 1000);
  }

  stop(): void {
    if (this.timer !== null) {
      this.clock.clearInterval(this.timer);
      this.timer = null;
    }
  }

  async flush(): Promise<void> {
    const total = Object.values(this.options.histograms).reduce(
      (sum: number, histogram: LatencyHistogram) => sum + histogram.count,
      0,
    );
    if (total === this.postedCount) {
      return;
    }
    const body = otlpMetricsBody({
      missionId: this.options.missionId,
      cell: this.options.cell,
      path: this.options.path,
      startTimeUnixNano: nanos(this.startMs),
      timeUnixNano: nanos(this.clock.nowMs()),
      histograms: this.options.histograms,
    });
    try {
      const result = await this.post(this.options.url, body);
      if (result.ok) {
        this.postedCount = total;
        return;
      }
      this.warn(`status ${String(result.status)}`);
    } catch (error: unknown) {
      this.warn(error instanceof Error ? error.name : "error");
    }
  }

  private warn(reason: string): void {
    if (this.warned) {
      return;
    }
    this.warned = true;
    console.warn(`The latency report was not accepted (${reason}). It is tried again at the next interval.`);
  }
}
