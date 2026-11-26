import { DEFAULT_LANGUAGE, LANGUAGES } from "./languages.ts";

export type MessageProblem = "missing" | "empty" | "unknown";

export interface MissingMessage {
  id: string;
  language: string;
  problem: MessageProblem;
}

export function findMissing(catalogues: Record<string, Record<string, string>>): MissingMessage[] {
  const english = catalogues[DEFAULT_LANGUAGE] ?? {};
  const ids = new Set<string>(Object.keys(english));
  for (const language of LANGUAGES) {
    for (const id of Object.keys(catalogues[language] ?? {})) ids.add(id);
  }
  const problems: MissingMessage[] = [];
  for (const id of [...ids].sort()) {
    for (const language of LANGUAGES) {
      const messages = catalogues[language] ?? {};
      if (!(id in english)) {
        if (id in messages) problems.push({ id, language, problem: "unknown" });
      } else if (!(id in messages)) {
        problems.push({ id, language, problem: "missing" });
      } else if ((messages[id] ?? "").trim() === "") {
        problems.push({ id, language, problem: "empty" });
      }
    }
  }
  return problems;
}
