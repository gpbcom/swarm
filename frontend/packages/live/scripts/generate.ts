import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

import { compile } from "json-schema-to-typescript";
import type { JSONSchema } from "json-schema-to-typescript";

export const SCHEMA_PATH: string = fileURLToPath(
  new URL("../../../../packages/python/swarm-models/schemas/swarm_models.schema.json", import.meta.url),
);
export const OUTPUT_PATH: string = fileURLToPath(new URL("../src/generated/models.ts", import.meta.url));
export const BANNER = `/* eslint-disable */
/**
 * This file was generated from swarm_models.schema.json by scripts/generate.ts.
 * Do not edit it by hand. Run pnpm --filter ./frontend/packages/live run generate.
 */
`;

export async function renderModels(schemaText: string): Promise<string> {
  const schema = JSON.parse(schemaText.replaceAll("#/$defs/", "#/definitions/")) as JSONSchema & {
    $defs?: Record<string, JSONSchema>;
  };
  const { $defs, ...rest } = schema;
  const prepared: JSONSchema = { ...rest, definitions: $defs ?? {} };
  return compile(prepared, "SwarmModels", {
    bannerComment: BANNER,
    unreachableDefinitions: true,
    additionalProperties: false,
  });
}

export async function isStale(schemaPath: string, outputPath: string): Promise<boolean> {
  const expected: string = await renderModels(await readFile(schemaPath, "utf-8"));
  try {
    return (await readFile(outputPath, "utf-8")) !== expected;
  } catch {
    return true;
  }
}

export async function writeModels(schemaPath: string, outputPath: string): Promise<void> {
  const text: string = await renderModels(await readFile(schemaPath, "utf-8"));
  await mkdir(dirname(outputPath), { recursive: true });
  await writeFile(outputPath, text, "utf-8");
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  if (process.argv.includes("--check")) {
    if (await isStale(SCHEMA_PATH, OUTPUT_PATH)) {
      console.error(
        `${OUTPUT_PATH} is out of date. Run pnpm --filter ./frontend/packages/live run generate to regenerate it.`,
      );
      process.exit(1);
    }
  } else {
    await writeModels(SCHEMA_PATH, OUTPUT_PATH);
  }
}
