import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { describe, it, expect } from "vitest";

const PACKAGE_FOLDER: string = fileURLToPath(new URL("..", import.meta.url));

function check(args: string[]): { status: number | null; stderr: string } {
  const result = spawnSync(
    process.execPath,
    ["--experimental-strip-types", "scripts/check-messages.ts", ...args],
    { cwd: PACKAGE_FOLDER, encoding: "utf-8" },
  );
  return { status: result.status, stderr: result.stderr };
}

describe("the message check", () => {
  it("fails on a folder with English only, and names the id and the languages", () => {
    const result = check(["--dir", "test/fixtures/english-only"]);
    expect(result.status).toBe(1);
    expect(result.stderr).toContain("sample.greeting");
    for (const language of ["fr", "de", "es"]) {
      expect(result.stderr).toContain(language);
    }
  });

  it("passes on a complete folder", () => {
    expect(check(["--dir", "test/fixtures/complete"]).status).toBe(0);
  });

  it("passes on the shipped messages", () => {
    expect(check([]).status).toBe(0);
  });
});
