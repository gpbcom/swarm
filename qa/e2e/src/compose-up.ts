import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import type { FullConfig } from "@playwright/test";

import { startBrowserServer } from "./browser-server.ts";

const REPOSITORY_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const COMPOSE_FILE = "infra/compose/e2e.yaml";
const COMPOSE_TIMEOUT_MS = 120_000;
const READY_DEADLINE_MS = 60_000;
const POLL_INTERVAL_MS = 1_000;
const CALL_TIMEOUT_MS = 5_000;
const HTTP_OK = 200;

/**
 * Start the compose service under test and the browser server of the pinned Playwright image, then wait until the
 * base URL answers 200.
 */
export default async function composeUp(config: FullConfig): Promise<void> {
  const service: unknown = config.metadata["composeService"];
  if (typeof service !== "string" || service === "") {
    throw new Error("The configuration metadata must name the composeService.");
  }
  const result = spawnSync("docker", ["compose", "-f", COMPOSE_FILE, "up", "-d", service], {
    cwd: REPOSITORY_ROOT,
    encoding: "utf8",
    timeout: COMPOSE_TIMEOUT_MS,
  });
  const output = `${result.stdout}${result.stderr}`;
  if (result.status !== 0) {
    throw new Error(`docker compose up failed:\n${output}`);
  }
  await startBrowserServer();
  const baseURL = config.projects[0]?.use.baseURL;
  if (baseURL === undefined) {
    throw new Error("The first project has no baseURL to wait for.");
  }
  const deadline = Date.now() + READY_DEADLINE_MS;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(baseURL, { signal: AbortSignal.timeout(CALL_TIMEOUT_MS) });
      if (response.status === HTTP_OK) {
        return;
      }
    } catch {
      // Not listening yet: poll again until the deadline.
    }
    await new Promise((done) => setTimeout(done, POLL_INTERVAL_MS));
  }
  throw new Error(`${baseURL} did not answer ${String(HTTP_OK)} within ${String(READY_DEADLINE_MS)} ms.\n${output}`);
}
