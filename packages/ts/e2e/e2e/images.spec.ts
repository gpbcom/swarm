import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

const REPOSITORY_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "..", "..");
const COMPOSE_FILE = "compose.e2e.yaml";

interface ComposeService {
  image?: string;
  build?: unknown;
}

interface ComposeConfig {
  services: Record<string, ComposeService>;
}

function compose(args: string[]): { status: number | null; stdout: string; stderr: string } {
  const result = spawnSync("docker", ["compose", "-f", COMPOSE_FILE, ...args], {
    cwd: REPOSITORY_ROOT,
    encoding: "utf8",
  });
  return { status: result.status, stdout: result.stdout, stderr: result.stderr };
}

test.describe("the real images", () => {
  test("are tagged with the image tag and never built", () => {
    const tag = process.env["SWARM_IMAGE_TAG"] ?? "";
    const result = compose(["config", "--format", "json"]);
    expect(result.status, result.stderr).toBe(0);
    const config = JSON.parse(result.stdout) as ComposeConfig;
    for (const service of Object.values(config.services)) {
      expect(service.image?.endsWith(`:${tag}`)).toBe(true);
      expect(service.build).toBeUndefined();
    }
  });

  test("start: the gateway runs and exits cleanly", () => {
    const result = compose(["run", "--rm", "--no-deps", "gateway"]);
    expect(result.status, result.stderr).toBe(0);
  });
});
