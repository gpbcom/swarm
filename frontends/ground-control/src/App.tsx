import { GroundControlFrame } from '@swarm/ui';
import type { ReactNode } from 'react';

export function App(): ReactNode {
  return <GroundControlFrame onHold={() => undefined} onAbort={() => undefined} />;
}
