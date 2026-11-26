import { describe, it, expect } from "vitest";

import { DEFAULT_LANGUAGE, LANGUAGES, LANGUAGE_NAMES, isLanguage, resolveLanguage } from "../src/languages.ts";

describe("the languages", () => {
  it("are English, French, German and Spanish", () => {
    expect([...LANGUAGES]).toEqual(["en", "fr", "de", "es"]);
    expect(DEFAULT_LANGUAGE).toBe("en");
  });

  it("have their endonyms", () => {
    expect(LANGUAGE_NAMES).toEqual({ en: "English", fr: "Français", de: "Deutsch", es: "Español" });
  });

  it.each(["en", "fr", "de", "es"])("accept %s", (value: string) => {
    expect(isLanguage(value)).toBe(true);
  });

  it.each(["it", "en-GB", "", "EN"])("refuse the string %s", (value: string) => {
    expect(isLanguage(value)).toBe(false);
  });

  it("refuse values that are not strings", () => {
    expect(isLanguage(null)).toBe(false);
    expect(isLanguage(undefined)).toBe(false);
    expect(isLanguage(4)).toBe(false);
  });

  it("resolve the language of the person when it is offered", () => {
    expect(resolveLanguage("de")).toBe("de");
    expect(resolveLanguage("fr")).toBe("fr");
  });

  it.each([null, undefined, "it", "en-GB"])("resolve %s to English", (value: string | null | undefined) => {
    expect(resolveLanguage(value)).toBe("en");
  });
});
