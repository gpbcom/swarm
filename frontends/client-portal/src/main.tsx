import "@swarm/tokens/tokens.css";
import "@swarm/ui/styles.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { I18nProvider } from "@swarm/i18n";

import { App } from "./App";

const root = document.getElementById("root");
if (root === null) {
  throw new Error("The #root element is missing from index.html.");
}
createRoot(root).render(
  <StrictMode>
    <I18nProvider language={undefined}>
      <App />
    </I18nProvider>
  </StrictMode>,
);
