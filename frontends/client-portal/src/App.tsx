import type { ReactNode } from "react";

import { ClientPortalFrame } from "@swarm/ui";

export function App(): ReactNode {
  return <ClientPortalFrame isSiteAgent={false} />;
}
