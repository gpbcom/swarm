export const LATENCY_BOUNDS_MS: readonly number[] = [10, 25, 50, 75, 100, 150, 200, 300, 400, 600, 800, 1000, 2000];

/** A fixed-bound latency histogram in milliseconds; a value equal to a bound falls in that bound's bucket. */
export class LatencyHistogram {
  readonly bounds: readonly number[];
  count = 0;
  sum = 0;
  min = Number.POSITIVE_INFINITY;
  max = Number.NEGATIVE_INFINITY;
  skipped = 0;
  private readonly counts: number[];

  constructor(bounds: readonly number[] = LATENCY_BOUNDS_MS) {
    this.bounds = bounds;
    this.counts = new Array<number>(bounds.length + 1).fill(0);
  }

  record(valueMs: number): void {
    if (!Number.isFinite(valueMs) || valueMs < 0) {
      this.skipped += 1;
      return;
    }
    let index = this.bounds.findIndex((bound: number) => valueMs <= bound);
    if (index < 0) {
      index = this.bounds.length;
    }
    this.counts[index] = (this.counts[index] ?? 0) + 1;
    this.count += 1;
    this.sum += valueMs;
    this.min = Math.min(this.min, valueMs);
    this.max = Math.max(this.max, valueMs);
  }

  bucketCounts(): number[] {
    return [...this.counts];
  }
}
