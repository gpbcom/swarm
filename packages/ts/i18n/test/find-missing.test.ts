import { describe, it, expect } from "vitest";

import { findMissing } from "../src/find-missing.ts";

const COMPLETE: Record<string, Record<string, string>> = {
  en: { "a.one": "One", "b.two": "Two" },
  fr: { "a.one": "Un", "b.two": "Deux" },
  de: { "a.one": "Eins", "b.two": "Zwei" },
  es: { "a.one": "Uno", "b.two": "Dos" },
};

describe("findMissing", () => {
  it("gives nothing for a complete set", () => {
    expect(findMissing(COMPLETE)).toEqual([]);
  });

  it("reports an id absent from a translation", () => {
    const catalogues = { ...COMPLETE, fr: { "a.one": "Un" } };
    expect(findMissing(catalogues)).toEqual([{ id: "b.two", language: "fr", problem: "missing" }]);
  });

  it("reports a blank message", () => {
    const catalogues = { ...COMPLETE, de: { "a.one": "  ", "b.two": "Zwei" } };
    expect(findMissing(catalogues)).toEqual([{ id: "a.one", language: "de", problem: "empty" }]);
  });

  it("reports an id that English does not have", () => {
    const catalogues = { ...COMPLETE, es: { ...COMPLETE["es"], "c.three": "Tres" } };
    expect(findMissing(catalogues)).toEqual([{ id: "c.three", language: "es", problem: "unknown" }]);
  });

  it("sorts by id, then in the order of the languages", () => {
    const catalogues = { ...COMPLETE, fr: {}, es: {}, de: { "b.two": "Zwei" } };
    expect(findMissing(catalogues)).toEqual([
      { id: "a.one", language: "fr", problem: "missing" },
      { id: "a.one", language: "de", problem: "missing" },
      { id: "a.one", language: "es", problem: "missing" },
      { id: "b.two", language: "fr", problem: "missing" },
      { id: "b.two", language: "es", problem: "missing" },
    ]);
  });
});
