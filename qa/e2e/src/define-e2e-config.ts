import { defineConfig } from "@playwright/test";
import type { PlaywrightTestConfig } from "@playwright/test";

const TAG_VARIABLE = "SWARM_IMAGE_TAG";
const BASE_URL_VARIABLE = "SWARM_E2E_BASE_URL";
const CI_VARIABLE = "CI";

export type E2eEnvironment = Record<string, string | undefined>;

/**
 * Build the Playwright configuration shared by every front end's end-to-end tests.
 * They run against the real images, so a missing image tag or a development server is refused.
 */
export function defineE2eConfig(
  options: PlaywrightTestConfig,
  env: E2eEnvironment = process.env,
): PlaywrightTestConfig {
  const tag = env[TAG_VARIABLE];
  if (tag === undefined || tag.trim() === "") {
    throw new Error(`${TAG_VARIABLE} must be set to the tag of the images under test.`);
  }
  if (options.webServer !== undefined) {
    throw new Error("A development server is refused: end-to-end tests run against the real images.");
  }
  const baseURL = env[BASE_URL_VARIABLE];
  const config: PlaywrightTestConfig = { ...options };
  if (baseURL) {
    config.use = { ...options.use, baseURL };
  }
  return defineConfig({
    ...config,
    forbidOnly: Boolean(env[CI_VARIABLE]),
    reporter: [["html", { outputFolder: "playwright-report", open: "never" }]],
  });
}
