import type { ReactNode } from 'react';

export interface Grid2Props {
  children?: ReactNode;
}

export function Grid2({ children }: Grid2Props): ReactNode {
  return <div className="grid-2">{children}</div>;
}
