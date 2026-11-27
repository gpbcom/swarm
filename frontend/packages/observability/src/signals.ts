import { context, trace, type Attributes } from "@opentelemetry/api";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { resourceFromAttributes } from "@opentelemetry/resources";
import {
  BasicTracerProvider,
  SimpleSpanProcessor,
  BatchSpanProcessor,
  type SpanExporter,
} from "@opentelemetry/sdk-trace-base";

import { redactAttributes, RedactingExporter } from "./redaction.ts";
import { parseTraceParent } from "./trace_parent.ts";

const SERVICE_NAME_KEY = "service.name";
const CELL_KEY = "cell";
const TRACES_PATH = "/v1/traces";

export interface SignalsOptions {
  serviceName: string;
  cell: string;
  exporter: SpanExporter;
  /** Batch the spans (production). Without it every span is exported when it ends. */
  batch?: boolean;
}

export interface StartSignalsOptions {
  serviceName: string;
  cell: string;
  /** The OTLP/HTTP base URL, without the signal path. */
  endpoint: string;
}

export interface Signals {
  continueTrace<T>(
    traceParent: string | null | undefined,
    name: string,
    attributes: Attributes,
    work: () => T,
  ): T;
  flush(): Promise<void>;
  shutdown(): Promise<void>;
}

/** Build the signals around any span exporter. */
export function createSignals(options: SignalsOptions): Signals {
  const exporter = new RedactingExporter(options.exporter);
  const processor = options.batch === true ? new BatchSpanProcessor(exporter) : new SimpleSpanProcessor(exporter);
  const provider = new BasicTracerProvider({
    resource: resourceFromAttributes({
      [SERVICE_NAME_KEY]: options.serviceName,
      [CELL_KEY]: options.cell,
    }),
    spanProcessors: [processor],
  });
  const tracer = provider.getTracer(options.serviceName);

  return {
    continueTrace<T>(
      traceParent: string | null | undefined,
      name: string,
      attributes: Attributes,
      work: () => T,
    ): T {
      const parent = parseTraceParent(traceParent);
      if (parent === undefined) {
        return work();
      }
      const parentContext = trace.setSpanContext(context.active(), parent);
      const span = tracer.startSpan(name, { attributes: redactAttributes(attributes) }, parentContext);
      try {
        return context.with(trace.setSpan(parentContext, span), work);
      } finally {
        span.end();
      }
    },
    flush: () => provider.forceFlush(),
    shutdown: () => provider.shutdown(),
  };
}

/** Start the signals, exported by OTLP/HTTP to `${endpoint}/v1/traces`. */
export function startSignals(options: StartSignalsOptions): Signals {
  const exporter = new OTLPTraceExporter({ url: `${options.endpoint}${TRACES_PATH}` });
  return createSignals({ serviceName: options.serviceName, cell: options.cell, exporter, batch: true });
}
