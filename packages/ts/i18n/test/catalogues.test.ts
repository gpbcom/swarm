import { describe, it, expect } from "vitest";

import { MESSAGES } from "../src/catalogues.ts";
import { findMissing } from "../src/find-missing.ts";
import { LANGUAGES } from "../src/languages.ts";

describe("the shipped catalogues", () => {
  it("hold one catalogue per language", () => {
    expect(Object.keys(MESSAGES).sort()).toEqual([...LANGUAGES].sort());
  });

  it("are complete in every language", () => {
    expect(findMissing(MESSAGES)).toEqual([]);
  });

  it("hold the status bar language message in English", () => {
    expect(MESSAGES.en["status.language"]).toBe("Language: {language}");
  });

  it.each(LANGUAGES)("hold the status bar language message in %s", (language) => {
    expect(MESSAGES[language]["status.language"]).toBeTruthy();
  });
});
