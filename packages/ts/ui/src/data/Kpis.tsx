import type { ReactNode } from "react";

export interface KpisProps {
  children?: ReactNode;
}

export interface KpiProps {
  value: ReactNode;
  label: ReactNode;
}

export function Kpis({ children }: KpisProps) {
  return <div className="kpis">{children}</div>;
}

export function Kpi({ value, label }: KpiProps) {
  return (
    <div className="kpi">
      <div className="value">{value}</div>
      <div className="label">{label}</div>
    </div>
  );
}
