import { TraceFlags, type SpanContext } from "@opentelemetry/api";

const TRACE_PARENT = /^00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$/;
const ZERO_TRACE_ID = "0".repeat(32);
const ZERO_SPAN_ID = "0".repeat(16);

/** Read a W3C `traceparent` value, or undefined when it is missing or invalid. */
export function parseTraceParent(value: string | null | undefined): SpanContext | undefined {
  if (typeof value !== "string") {
    return undefined;
  }
  const match = TRACE_PARENT.exec(value);
  if (match === null) {
    return undefined;
  }
  const [, traceId, spanId, flags] = match;
  if (traceId === undefined || spanId === undefined || flags === undefined) {
    return undefined;
  }
  if (traceId === ZERO_TRACE_ID || spanId === ZERO_SPAN_ID) {
    return undefined;
  }
  return {
    traceId,
    spanId,
    isRemote: true,
    traceFlags: parseInt(flags, 16) & TraceFlags.SAMPLED,
  };
}
