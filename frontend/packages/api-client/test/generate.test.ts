import assert from "node:assert/strict";
import { spawnSync, type SpawnSyncReturns } from "node:child_process";
import { appendFile, copyFile, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, before, beforeEach, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const FIXTURE_PATH: string = fileURLToPath(new URL("./fixtures/sample.openapi.json", import.meta.url));
const PACKAGE_DIR: string = fileURLToPath(new URL("..", import.meta.url));
const SCRIPT_PATH: string = join(PACKAGE_DIR, "scripts", "generate.ts");

function run(args: string[], cwd: string): SpawnSyncReturns<string> {
  return spawnSync("node", ["--experimental-strip-types", SCRIPT_PATH, ...args], { cwd, encoding: "utf-8" });
}

describe("the api client generator", () => {
  let folder = "";
  let outDir = "";
  let options: string[] = [];

  before(async () => {
    folder = await mkdtemp(join(tmpdir(), "api-client-generate-"));
  });

  after(async () => {
    await rm(folder, { recursive: true, force: true });
  });

  beforeEach(async () => {
    const openapiDir: string = join(folder, "openapi");
    outDir = join(folder, "generated");
    await rm(outDir, { recursive: true, force: true });
    await mkdir(openapiDir, { recursive: true });
    await copyFile(FIXTURE_PATH, join(openapiDir, "sample.json"));
    options = ["--openapi", openapiDir, "--out", outDir];
  });

  it("writes one file per document", async () => {
    const result = run(options, folder);
    assert.equal(result.status, 0, result.stderr);
    const text: string = await readFile(join(outDir, "sample.ts"), "utf-8");
    assert.ok(text.length > 0);
  });

  it("checks clean right after a generation", () => {
    run(options, folder);
    const result = run([...options, "--check"], folder);
    assert.equal(result.status, 0, result.stderr);
  });

  it("fails the check and names the file after a generated file is edited", async () => {
    run(options, folder);
    await appendFile(join(outDir, "sample.ts"), "// edited\n");
    const result = run([...options, "--check"], folder);
    assert.equal(result.status, 1);
    assert.match(result.stderr, /sample\.ts/);
  });

  it("fails the check when a generated file has no document", async () => {
    run(options, folder);
    await writeFile(join(outDir, "old.ts"), "// stale\n");
    const result = run([...options, "--check"], folder);
    assert.equal(result.status, 1);
    assert.match(result.stderr, /old\.ts/);
  });

  it("checks the package's own generated clients with the default folders", () => {
    const result = run(["--check"], PACKAGE_DIR);
    assert.equal(result.status, 0, result.stderr);
  });
});
