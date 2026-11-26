import { act, render, screen } from "@testing-library/react";
import { useEffect, useRef } from "react";
import type { ReactElement } from "react";
import { createIntl, useIntl } from "react-intl";
import { afterEach, describe, expect, it } from "vitest";

import { MESSAGES } from "../src/catalogues.ts";
import { I18nProvider, useLanguage } from "../src/i18n-provider.tsx";
import type { Language } from "../src/languages.ts";
import { LANGUAGE_NAMES } from "../src/languages.ts";

const MESSAGE_ID = "status.language";
const TEST_ID = "status";

function expectedText(language: Language): string {
  const intl = createIntl({ locale: language, messages: MESSAGES[language] });
  return intl.formatMessage({ id: MESSAGE_ID }, { language: LANGUAGE_NAMES[language] });
}

interface ProbeProps {
  mounts: { count: number };
  onSwitch: { current: (language: Language) => void };
}

function Probe({ mounts, onSwitch }: ProbeProps): ReactElement {
  const intl = useIntl();
  const { language, setLanguage } = useLanguage();
  const counted = useRef(false);
  onSwitch.current = setLanguage;
  useEffect(() => {
    if (!counted.current) {
      counted.current = true;
      mounts.count += 1;
    }
  }, [mounts]);
  return (
    <span data-testid={TEST_ID}>
      {intl.formatMessage({ id: MESSAGE_ID }, { language: LANGUAGE_NAMES[language] })}
    </span>
  );
}

function renderProbe(language: string | null | undefined): ProbeProps {
  const props: ProbeProps = { mounts: { count: 0 }, onSwitch: { current: () => undefined } };
  render(
    <I18nProvider language={language}>
      <Probe {...props} />
    </I18nProvider>,
  );
  return props;
}

describe("the I18nProvider", () => {
  afterEach(() => {
    document.documentElement.lang = "";
  });

  it("shows the language of the signed-in person from the first render", () => {
    renderProbe("de");
    expect(screen.getByTestId(TEST_ID).textContent).toBe(expectedText("de"));
    expect(expectedText("de")).not.toBe(expectedText("en"));
  });

  it.each([[undefined], [null], ["it"]])("shows English for the language %s", (language) => {
    renderProbe(language);
    expect(screen.getByTestId(TEST_ID).textContent).toBe(expectedText("en"));
  });

  it("sets the language of the document after the first render", () => {
    renderProbe("de");
    expect(document.documentElement.lang).toBe("de");
  });

  it("switches language without a reload or a remount", () => {
    const props = renderProbe("de");
    const element = screen.getByTestId(TEST_ID);
    const href = window.location.href;

    act(() => {
      props.onSwitch.current("fr");
    });

    expect(screen.getByTestId(TEST_ID)).toBe(element);
    expect(element.textContent).toBe(expectedText("fr"));
    expect(props.mounts.count).toBe(1);
    expect(document.documentElement.lang).toBe("fr");
    expect(window.location.href).toBe(href);
  });
});
