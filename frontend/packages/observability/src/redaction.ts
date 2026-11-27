import type { Attributes } from "@opentelemetry/api";
import type { ReadableSpan, SpanExporter } from "@opentelemetry/sdk-trace-base";

const SENSITIVE_PARTS: readonly string[] = [
  "authorization",
  "cookie",
  "password",
  "secret",
  "token",
  "credential",
  "api_key",
  "email",
  "phone",
  "enduser",
  "url.query",
];

/** Tell whether an attribute key may carry a secret or personal data. */
export function isSensitiveKey(key: string): boolean {
  const lower = key.toLowerCase();
  return SENSITIVE_PARTS.some((part) => lower.includes(part));
}

/** Copy the attributes without the sensitive ones. */
export function redactAttributes(attributes: Attributes): Attributes {
  const kept: Attributes = {};
  for (const [key, value] of Object.entries(attributes)) {
    if (!isSensitiveKey(key)) {
      kept[key] = value;
    }
  }
  return kept;
}

/** An exporter that removes the sensitive attributes of every span before it exports it. */
export class RedactingExporter implements SpanExporter {
  private readonly inner: SpanExporter;

  constructor(inner: SpanExporter) {
    this.inner = inner;
  }

  export(spans: ReadableSpan[], resultCallback: Parameters<SpanExporter["export"]>[1]): void {
    const redacted = spans.map(
      (span) =>
        Object.create(span as object, {
          attributes: { value: redactAttributes(span.attributes) },
        }) as ReadableSpan,
    );
    this.inner.export(redacted, resultCallback);
  }

  shutdown(): Promise<void> {
    return this.inner.shutdown();
  }

  async forceFlush(): Promise<void> {
    await this.inner.forceFlush?.();
  }
}
