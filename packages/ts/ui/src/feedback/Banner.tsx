import type { ReactNode } from "react";

export type BannerKind = "success" | "failure" | "decision" | "system";

export interface BannerProps {
  kind: BannerKind;
  icon: ReactNode;
  children: ReactNode;
}

const ALERT_KINDS: readonly BannerKind[] = ["failure", "decision"];

export function Banner({ kind, icon, children }: BannerProps) {
  const role = ALERT_KINDS.includes(kind) ? "alert" : "status";
  return (
    <div className={`banner ${kind}`} role={role}>
      <span aria-hidden="true">{icon}</span>
      <span>{children}</span>
    </div>
  );
}
