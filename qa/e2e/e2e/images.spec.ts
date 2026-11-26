import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

const REPOSITORY_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
const COMPOSE_FILE = "infra/compose/e2e.yaml";
// A container that never exits fails its test instead of holding the job until GitHub cancels it.
const COMPOSE_TIMEOUT_MS = 120_000;
// The gateway image serves until stopped, so its start is checked by importing its app's main() and exiting.
const GATEWAY_COMMAND = "python";
const GATEWAY_IMPORT = ["-c", "import swarm_gateway.main"];

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
    timeout: COMPOSE_TIMEOUT_MS,
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

  test("start: the gateway's app imports and exits cleanly", () => {
    const entrypoint = ["--entrypoint", GATEWAY_COMMAND];
    const result = compose(["run", "--rm", "--no-deps", ...entrypoint, "gateway", ...GATEWAY_IMPORT]);
    expect(result.status, result.stderr).toBe(0);
  });
});
