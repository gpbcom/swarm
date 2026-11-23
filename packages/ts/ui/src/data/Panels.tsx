import type { ReactNode } from "react";

export interface PanelsProps {
  children?: ReactNode;
}

export function Split({ children }: PanelsProps) {
  return <div className="split">{children}</div>;
}

export function Panel({ children }: PanelsProps) {
  return <div className="panel">{children}</div>;
}
