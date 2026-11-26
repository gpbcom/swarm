import type { ReactNode } from "react";

export interface EmptyStateProps {
  icon: ReactNode;
  message: ReactNode;
  action?: ReactNode;
}

export function EmptyState({ icon, message, action }: EmptyStateProps) {
  return (
    <div className="empty">
      <span aria-hidden="true">{icon}</span>
      <p>{message}</p>
      {action}
    </div>
  );
}
