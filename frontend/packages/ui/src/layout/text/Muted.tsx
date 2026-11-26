import type { ReactNode } from 'react';

export interface MutedProps {
  children?: ReactNode;
}

export function Muted({ children }: MutedProps): ReactNode {
  return <span className="muted">{children}</span>;
}
