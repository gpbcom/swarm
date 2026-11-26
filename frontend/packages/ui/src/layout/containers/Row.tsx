import type { ReactNode } from 'react';

export interface RowProps {
  children?: ReactNode;
}

export function Row({ children }: RowProps): ReactNode {
  return <div className="row">{children}</div>;
}
