import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const REPOSITORY_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "..", "..");
const COMPOSE_FILE = "infra/compose/e2e.yaml";
const SERVICE = "ground-control";
const BASE_URL = process.env["SWARM_E2E_BASE_URL"] ?? "http://127.0.0.1:8180";
const READY_TIMEOUT_MS = 120_000;
const POLL_INTERVAL_MS = 1_000;
const COMPOSE_TIMEOUT_MS = 120_000;

function compose(args: string[]): void {
  const result = spawnSync("docker", ["compose", "-f", COMPOSE_FILE, ...args], {
    cwd: REPOSITORY_ROOT,
    encoding: "utf8",
    timeout: COMPOSE_TIMEOUT_MS,
  });
  if (result.status !== 0) {
    throw new Error(`docker compose ${args.join(" ")} failed: ${result.stderr}`);
  }
}

async function answers(): Promise<boolean> {
  try {
    const response = await fetch(BASE_URL);
    return response.status === 200;
  } catch {
    return false;
  }
}

async function waitUntilReady(): Promise<void> {
  const deadline = Date.now() + READY_TIMEOUT_MS;
  while (Date.now() < deadline) {
    if (await answers()) {
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
  }
  throw new Error(`${BASE_URL} did not answer 200 within ${String(READY_TIMEOUT_MS / 1000)} s.`);
}

export default async function globalSetup(): Promise<() => Promise<void>> {
  compose(["up", "-d", SERVICE]);
  await waitUntilReady();
  return () => {
    compose(["rm", "-sf", SERVICE]);
    return Promise.resolve();
  };
}
