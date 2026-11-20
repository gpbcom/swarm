import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { basename, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { renderClient } from "./render.ts";

const JSON_EXTENSION = ".json";
const TS_EXTENSION = ".ts";
const DEFAULT_OPENAPI: string = fileURLToPath(new URL("../openapi/", import.meta.url));
const DEFAULT_OUT: string = fileURLToPath(new URL("../src/generated/", import.meta.url));

function option(args: string[], flag: string, fallback: string): string {
  const index: number = args.indexOf(flag);
  const value: string | undefined = index >= 0 ? args[index + 1] : undefined;
  return value === undefined ? fallback : resolve(value);
}

async function names(dir: string, extension: string): Promise<string[]> {
  try {
    const files: string[] = await readdir(dir);
    return files
      .filter((file) => file.endsWith(extension))
      .map((file) => basename(file, extension))
      .sort();
  } catch {
    return [];
  }
}

async function main(args: string[]): Promise<number> {
  const openapiDir: string = option(args, "--openapi", DEFAULT_OPENAPI);
  const outDir: string = option(args, "--out", DEFAULT_OUT);
  const check: boolean = args.includes("--check");
  const documents: string[] = await names(openapiDir, JSON_EXTENSION);
  const problems: string[] = [];
  if (!check) {
    await mkdir(outDir, { recursive: true });
  }
  for (const name of documents) {
    const document = JSON.parse(await readFile(join(openapiDir, name + JSON_EXTENSION), "utf-8")) as object;
    const expected: string = await renderClient(document, name);
    const target: string = join(outDir, name + TS_EXTENSION);
    if (!check) {
      await writeFile(target, expected, "utf-8");
      continue;
    }
    let current: string | undefined;
    try {
      current = await readFile(target, "utf-8");
    } catch {
      problems.push(`${target} is missing.`);
      continue;
    }
    if (current !== expected) {
      problems.push(`${target} is stale.`);
    }
  }
  if (!check) {
    return 0;
  }
  for (const name of await names(outDir, TS_EXTENSION)) {
    if (!documents.includes(name)) {
      problems.push(`${join(outDir, name + TS_EXTENSION)} has no document in ${openapiDir}.`);
    }
  }
  for (const problem of problems) {
    console.error(problem);
  }
  if (problems.length > 0) {
    console.error("Run pnpm --filter ./packages/ts/api-client run generate to regenerate.");
    return 1;
  }
  return 0;
}

process.exitCode = await main(process.argv.slice(2));
