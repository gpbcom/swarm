import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { findMissing } from "../src/find-missing.ts";
import { LANGUAGES } from "../src/languages.ts";

const PACKAGE_FOLDER: string = fileURLToPath(new URL("..", import.meta.url));
const DEFAULT_DIR = "src/messages";

const dirIndex = process.argv.indexOf("--dir");
const dirArgument = dirIndex >= 0 ? process.argv[dirIndex + 1] : undefined;
const folder = resolve(PACKAGE_FOLDER, dirArgument ?? DEFAULT_DIR);

const catalogues: Record<string, Record<string, string>> = {};
for (const language of LANGUAGES) {
  catalogues[language] = JSON.parse(readFileSync(join(folder, `${language}.json`), "utf-8")) as Record<
    string,
    string
  >;
}

const problems = findMissing(catalogues);
if (problems.length > 0) {
  for (const { id, language, problem } of problems) {
    process.stderr.write(`${problem}: ${id} (${language})\n`);
  }
  process.exit(1);
}
process.stdout.write(`All ${String(LANGUAGES.length)} languages hold the same messages.\n`);
