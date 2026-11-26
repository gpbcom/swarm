import type { ReactNode } from "react";

export type ChecklistStatus = "ok" | "fail" | "pending";

export interface ChecklistItem {
  label: ReactNode;
  status: ChecklistStatus;
}

export interface ChecklistProps {
  items: readonly ChecklistItem[];
}

const PREFIXES: Readonly<Record<ChecklistStatus, string>> = {
  ok: "✅",
  fail: "❌",
  pending: "⏳",
};

export function Checklist({ items }: ChecklistProps) {
  return (
    <ul className="checklist">
      {items.map((item, index) => (
        <li key={index} className={`check ${item.status}`}>
          <span aria-hidden="true">{PREFIXES[item.status]}</span>
          <span>{item.label}</span>
        </li>
      ))}
    </ul>
  );
}
