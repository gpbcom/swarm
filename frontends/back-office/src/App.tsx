import { BackOfficeFrame } from "@swarm/ui";
import { LANGUAGE_NAMES, useLanguage } from "@swarm/i18n";
import { useIntl } from "react-intl";
import type { ReactNode } from "react";

export function App(): ReactNode {
  const intl = useIntl();
  const { language } = useLanguage();
  const statusItems = [
    intl.formatMessage({ id: "status.language" }, { language: LANGUAGE_NAMES[language] }),
  ];
  return <BackOfficeFrame statusItems={statusItems} />;
}
