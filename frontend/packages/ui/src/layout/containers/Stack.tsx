import type { ReactNode } from 'react';

export interface StackProps {
  children?: ReactNode;
}

export function Stack({ children }: StackProps): ReactNode {
  return <div className="stack">{children}</div>;
}
