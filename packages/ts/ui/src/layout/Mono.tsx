import type { ReactNode } from 'react';

export interface MonoProps {
  children?: ReactNode;
}

export function Mono({ children }: MonoProps): ReactNode {
  return <span className="mono">{children}</span>;
}
