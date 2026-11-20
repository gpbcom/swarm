import * as RadixProgress from "@radix-ui/react-progress";

export type ProgressKind = "success" | "failure" | "decision";

export interface ProgressProps {
  value: number;
  label: string;
  kind?: ProgressKind;
}

const STEP = 10;

export function Progress({ value, label, kind }: ProgressProps) {
  const step = Math.round(value / STEP) * STEP;
  const indicator = step > 0 ? `p${String(step)}` : undefined;
  const rootClass = kind === undefined ? "progress" : `progress ${kind}`;
  return (
    <RadixProgress.Root className={rootClass} value={value} aria-label={label}>
      <RadixProgress.Indicator asChild>
        <span className={indicator} />
      </RadixProgress.Indicator>
    </RadixProgress.Root>
  );
}
