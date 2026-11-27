import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import type { FullConfig } from "@playwright/test";

import { stopBrowserServer } from "./browser-server.ts";

const REPOSITORY_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const COMPOSE_FILE = "infra/compose/e2e.yaml";
const COMPOSE_TIMEOUT_MS = 120_000;

/**
 * Stop and remove the compose service and the browser server the visual tests started.
 */
export default function composeDown(config: FullConfig): void {
  stopBrowserServer();
  const service: unknown = config.metadata["composeService"];
  if (typeof service !== "string" || service === "") {
    throw new Error("The configuration metadata must name the composeService.");
  }
  const result = spawnSync("docker", ["compose", "-f", COMPOSE_FILE, "rm", "--stop", "--force", service], {
    cwd: REPOSITORY_ROOT,
    encoding: "utf8",
    timeout: COMPOSE_TIMEOUT_MS,
  });
  if (result.status !== 0) {
    throw new Error(`docker compose rm failed:\n${result.stdout}${result.stderr}`);
  }
}
