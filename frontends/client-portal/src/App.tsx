import { LANGUAGE_NAMES, useLanguage } from "@swarm/i18n";
import { useIntl } from "react-intl";
import type { ReactNode } from "react";

import { ClientPortalFrame } from "@swarm/ui";

export function App(): ReactNode {
  const intl = useIntl();
  const { language } = useLanguage();
  const statusItems = [
    intl.formatMessage({ id: "status.language" }, { language: LANGUAGE_NAMES[language] }),
  ];
  return <ClientPortalFrame statusItems={statusItems} isSiteAgent={false} />;
}
