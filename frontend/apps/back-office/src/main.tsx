import "@swarm/tokens/tokens.css";
import "@swarm/ui/styles.css";

import { StrictMode, useMemo } from "react";
import { createRoot } from "react-dom/client";

import { I18nProvider } from "@swarm/i18n";

import { App } from "./App";
import { GatewayProvider } from "./api/GatewayProvider";
import { createBackOfficeGateway } from "./api/gateway";
import { SignInGate } from "./auth/SignInGate";
import { useSession } from "./auth/SessionProvider";
import { config } from "./config";
import type { ReactNode } from "react";

function SignedIn(): ReactNode {
  const session = useSession();
  const client = useMemo(
    () =>
      createBackOfficeGateway({
        baseUrl: config.gatewayUrl,
        accessToken: session.accessToken,
      }),
    [session.accessToken],
  );
  return (
    <GatewayProvider client={client}>
      <App />
    </GatewayProvider>
  );
}

const root = document.getElementById("root");
if (root === null) {
  throw new Error("The #root element is missing from index.html.");
}
createRoot(root).render(
  <StrictMode>
    <I18nProvider language={undefined}>
      <SignInGate>
        <SignedIn />
      </SignInGate>
    </I18nProvider>
  </StrictMode>,
);
