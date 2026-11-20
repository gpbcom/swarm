import type { ReactNode } from 'react';

export interface SpacerProps {
  children?: ReactNode;
}

export function Spacer({ children }: SpacerProps): ReactNode {
  return <div className="spacer">{children}</div>;
}
