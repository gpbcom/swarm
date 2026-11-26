import { useContext, useEffect, useMemo, useState } from "react";
import type { ReactElement, ReactNode } from "react";
import { IntlProvider } from "react-intl";

import { MESSAGES } from "./catalogues.ts";
import { LanguageContext } from "./language-context.ts";
import type { LanguageContextValue } from "./language-context.ts";
import { DEFAULT_LANGUAGE, resolveLanguage } from "./languages.ts";
import type { Language } from "./languages.ts";

export interface I18nProviderProps {
  language: string | null | undefined;
  children: ReactNode;
}

export function I18nProvider({ language, children }: I18nProviderProps): ReactElement {
  const [current, setCurrent] = useState<Language>(() => resolveLanguage(language));
  const [applied, setApplied] = useState(language);

  if (applied !== language) {
    setApplied(language);
    setCurrent(resolveLanguage(language));
  }

  useEffect(() => {
    document.documentElement.lang = current;
  }, [current]);

  const value = useMemo<LanguageContextValue>(
    () => ({ language: current, setLanguage: setCurrent }),
    [current],
  );

  return (
    <LanguageContext.Provider value={value}>
      <IntlProvider locale={current} messages={MESSAGES[current]} defaultLocale={DEFAULT_LANGUAGE}>
        {children}
      </IntlProvider>
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextValue {
  const value = useContext(LanguageContext);
  if (value === null) {
    throw new Error("useLanguage must be used inside an I18nProvider.");
  }
  return value;
}
