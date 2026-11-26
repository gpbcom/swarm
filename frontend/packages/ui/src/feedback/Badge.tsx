import type { ReactNode } from "react";

export type BadgeKind = "persona" | "entity" | "system" | "success" | "failure" | "decision" | "action";

export interface BadgeProps {
  kind: BadgeKind;
  icon: ReactNode;
  label: ReactNode;
}

export function Badge({ kind, icon, label }: BadgeProps) {
  return (
    <span className={`badge ${kind}`}>
      <span aria-hidden="true">{icon}</span>
      {label}
    </span>
  );
}
