import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { connect } from "node:net";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SHARED_PACKAGE = join(HERE, "../package.json");
const PLAYWRIGHT_PACKAGE = "@playwright/test";
const CONTAINER = "swarm-e2e-browser";
const HOST = "127.0.0.1";
const PORT = 8190;
const DOCKER_TIMEOUT_MS = 600_000;
const READY_DEADLINE_MS = 180_000;
const POLL_INTERVAL_MS = 1_000;

function sharedPlaywrightVersion(): string {
  const shared = JSON.parse(readFileSync(SHARED_PACKAGE, "utf-8")) as { devDependencies?: Record<string, string> };
  const version = shared.devDependencies?.[PLAYWRIGHT_PACKAGE];
  if (version === undefined || !/^\d+\.\d+\.\d+$/.test(version)) {
    throw new Error(`${SHARED_PACKAGE} must pin ${PLAYWRIGHT_PACKAGE} to an exact version.`);
  }
  return version;
}

/** The exact Playwright version of the shared set-up, which the browser image follows. */
export const PLAYWRIGHT_VERSION = sharedPlaywrightVersion();

/** The official Playwright image whose Chromium and fonts render every visual test, in CI and locally alike. */
export const BROWSER_IMAGE = `mcr.microsoft.com/playwright:v${PLAYWRIGHT_VERSION}-noble`;

/** Where the tests reach the browser server of that image. */
export const BROWSER_WS_ENDPOINT = `ws://${HOST}:${String(PORT)}/`;

function docker(args: string[]): string {
  const result = spawnSync("docker", args, { encoding: "utf8", timeout: DOCKER_TIMEOUT_MS });
  const output = `${result.stdout}${result.stderr}`;
  if (result.status !== 0) {
    throw new Error(`docker ${args[0] ?? ""} failed:\n${output}`);
  }
  return output;
}

function listening(): Promise<boolean> {
  return new Promise((answer) => {
    const socket = connect({ host: HOST, port: PORT });
    socket.once("connect", () => {
      socket.destroy();
      answer(true);
    });
    socket.once("error", () => {
      socket.destroy();
      answer(false);
    });
  });
}

/**
 * Start the browser server of the pinned Playwright image, on the host network so that it reaches the front end under
 * test on the loopback, then wait until it listens.
 */
export async function startBrowserServer(): Promise<void> {
  stopBrowserServer();
  docker([
    "run",
    "--detach",
    "--rm",
    "--init",
    "--ipc=host",
    "--network=host",
    "--name",
    CONTAINER,
    "--user",
    "pwuser",
    "--workdir",
    "/home/pwuser",
    BROWSER_IMAGE,
    "/bin/sh",
    "-c",
    `npx -y playwright@${PLAYWRIGHT_VERSION} run-server --port ${String(PORT)} --host ${HOST}`,
  ]);
  const deadline = Date.now() + READY_DEADLINE_MS;
  while (Date.now() < deadline) {
    if (await listening()) {
      return;
    }
    await new Promise((done) => setTimeout(done, POLL_INTERVAL_MS));
  }
  const logs = spawnSync("docker", ["logs", CONTAINER], { encoding: "utf8" });
  throw new Error(
    `The browser server of ${BROWSER_IMAGE} did not listen on ${BROWSER_WS_ENDPOINT} within ` +
      `${String(READY_DEADLINE_MS)} ms.\n${logs.stdout}${logs.stderr}`,
  );
}

/** Stop and remove the browser server, whether it runs or not. */
export function stopBrowserServer(): void {
  spawnSync("docker", ["rm", "--force", CONTAINER], { encoding: "utf8", timeout: DOCKER_TIMEOUT_MS });
}
