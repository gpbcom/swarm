import type { LatencyHistogram } from "./latency-histogram.ts";

export const TELEMETRY_METRICS = {
  droneToScreen: "swarm.telemetry.drone_to_screen",
  frameToPixels: "swarm.live.frame_to_pixels",
} as const;

export type LivePath = "edge" | "cell";

export interface OtlpMetricsInput {
  missionId: string | null;
  cell: string | null;
  path: LivePath;
  startTimeUnixNano: string;
  timeUnixNano: string;
  histograms: Record<string, LatencyHistogram>;
}

interface Attribute {
  key: string;
  value: { stringValue: string };
}

const AGGREGATION_TEMPORALITY_CUMULATIVE = 2;

function attribute(key: string, value: string): Attribute {
  return { key, value: { stringValue: value } };
}

/** The OTLP/HTTP JSON ExportMetricsServiceRequest of the latency histograms, as text. */
export function otlpMetricsBody(input: OtlpMetricsInput): string {
  const resource: Attribute[] = [attribute("service.name", "ground-control")];
  if (input.missionId !== null) {
    resource.push(attribute("mission_id", input.missionId));
  }
  if (input.cell !== null) {
    resource.push(attribute("cell", input.cell));
  }
  const metrics = Object.entries(input.histograms).map(([name, histogram]: [string, LatencyHistogram]) => {
    const point: Record<string, unknown> = {
      attributes: [attribute("swarm.live.path", input.path)],
      startTimeUnixNano: input.startTimeUnixNano,
      timeUnixNano: input.timeUnixNano,
      count: String(histogram.count),
      sum: histogram.sum,
      bucketCounts: histogram.bucketCounts().map((value: number) => String(value)),
      explicitBounds: [...histogram.bounds],
    };
    if (histogram.count > 0) {
      point["min"] = histogram.min;
      point["max"] = histogram.max;
    }
    return {
      name,
      unit: "ms",
      histogram: { aggregationTemporality: AGGREGATION_TEMPORALITY_CUMULATIVE, dataPoints: [point] },
    };
  });
  return JSON.stringify({
    resourceMetrics: [
      { resource: { attributes: resource }, scopeMetrics: [{ scope: { name: "@swarm/live" }, metrics }] },
    ],
  });
}
