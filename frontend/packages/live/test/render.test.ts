import assert from "node:assert/strict";
import { appendFile, mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, before, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

import { BANNER, OUTPUT_PATH, SCHEMA_PATH, isStale, renderModels, writeModels } from "../scripts/generate.ts";

const FIXTURE_PATH: string = fileURLToPath(new URL("./fixtures/sample.schema.json", import.meta.url));

describe("the live models generator", () => {
  let folder = "";
  let fixtureText = "";

  before(async () => {
    folder = await mkdtemp(join(tmpdir(), "live-generate-"));
    fixtureText = await readFile(FIXTURE_PATH, "utf-8");
  });

  after(async () => {
    await rm(folder, { recursive: true, force: true });
  });

  it("starts the render with the banner", async () => {
    const text: string = await renderModels(fixtureText);
    assert.ok(text.startsWith(BANNER));
  });

  it("renders one exported type per definition", async () => {
    const text: string = await renderModels(fixtureText);
    assert.match(text, /export interface Sample\b/);
    assert.match(text, /export type SampleState =\s*"on"\s*\|\s*"off"/);
  });

  it("renders the same text twice", async () => {
    const first: string = await renderModels(fixtureText);
    const second: string = await renderModels(fixtureText);
    assert.equal(first, second);
  });

  it("rejects invalid JSON", async () => {
    await assert.rejects(renderModels("{not json"));
  });

  it("is stale when the output is missing", async () => {
    assert.equal(await isStale(FIXTURE_PATH, join(folder, "missing.ts")), true);
  });

  it("writes into missing folders and is then fresh", async () => {
    const output: string = join(folder, "a", "b", "models.ts");
    await writeModels(FIXTURE_PATH, output);
    assert.equal(await isStale(FIXTURE_PATH, output), false);
    assert.equal(await readFile(output, "utf-8"), await renderModels(fixtureText));
  });

  it("is stale again after the output is edited", async () => {
    const output: string = join(folder, "edited.ts");
    await writeModels(FIXTURE_PATH, output);
    await appendFile(output, "// edited\n");
    assert.equal(await isStale(FIXTURE_PATH, output), true);
  });

  it("points at the schema and the generated file", () => {
    assert.ok(SCHEMA_PATH.endsWith("swarm-models/schemas/swarm_models.schema.json"));
    assert.ok(OUTPUT_PATH.endsWith("live/src/generated/models.ts"));
  });
});
