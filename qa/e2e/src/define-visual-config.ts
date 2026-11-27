import { readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import type { PlaywrightTestConfig } from "@playwright/test";

import { BROWSER_WS_ENDPOINT } from "./browser-server.ts";
import { defineE2eConfig } from "./define-e2e-config.ts";
import type { E2eEnvironment } from "./define-e2e-config.ts";

export const LIGHT_PROJECT = "light";
export const DARK_PROJECT = "dark";
export const VISUAL_MAX_DIFF_PIXEL_RATIO = 0.02;
export const VISUAL_THRESHOLD = 0.2;

const HERE = dirname(fileURLToPath(import.meta.url));
const REPOSITORY_ROOT = resolve(HERE, "../../..");
const TOKENS_FILE = join(REPOSITORY_ROOT, "frontend/packages/tokens/src/tokens.css");
const SCREENS_TEMPLATE = join(REPOSITORY_ROOT, "docs/specs/screens", "{arg}{ext}");
const DARK_SUFFIX = ".dark";
const LOCALE = "en-GB";
const TIME_ZONE = "UTC";

export interface VisualOptions extends PlaywrightTestConfig {
  /** The service of `infra/compose/e2e.yaml` that serves the front end under test. */
  composeService: string;
}

export type VisualConfig = PlaywrightTestConfig & { metadata: { composeService: string } };

function pixelToken(css: string, name: string): number {
  const match = new RegExp(`--${name}:\\s*(\\d+)px`).exec(css);
  if (match?.[1] === undefined) {
    throw new Error(`The token --${name} is missing from ${TOKENS_FILE}.`);
  }
  return Number(match[1]);
}

/**
 * The name of a screenshot, relative to `docs/specs/screens`, for a use case, a node and a project.
 */
export function screenshotName(useCase: string, node: string, project: string): string {
  if (project === LIGHT_PROJECT) {
    return `${useCase}/${node}`;
  }
  if (project === DARK_PROJECT) {
    return `${useCase}/${node}${DARK_SUFFIX}`;
  }
  throw new Error(`Unknown project ${JSON.stringify(project)}: expected ${LIGHT_PROJECT} or ${DARK_PROJECT}.`);
}

/**
 * Build the Playwright configuration shared by the visual tests of every front end: a light and a dark project at
 * the screen size of the tokens, screens stored in the specification folder, and the compose stack started around them.
 * Both projects render in the browser of the pinned Playwright image, so that a screen captured on any machine has the
 * pixels CI compares it with.
 */
export function defineVisualConfig(
  options: VisualOptions,
  env: E2eEnvironment = process.env,
): VisualConfig {
  const { composeService, ...rest } = options;
  const css = readFileSync(TOKENS_FILE, "utf-8");
  const viewport = { width: pixelToken(css, "screen-width"), height: pixelToken(css, "screen-height") };
  const common = {
    viewport,
    deviceScaleFactor: 1,
    locale: LOCALE,
    timezoneId: TIME_ZONE,
    connectOptions: { wsEndpoint: BROWSER_WS_ENDPOINT },
  };
  const config = defineE2eConfig(
    {
      ...rest,
      projects: [
        { name: LIGHT_PROJECT, use: { ...common, colorScheme: "light" } },
        { name: DARK_PROJECT, use: { ...common, colorScheme: "dark" } },
      ],
      snapshotPathTemplate: SCREENS_TEMPLATE,
      updateSnapshots: "none",
      expect: {
        toHaveScreenshot: {
          maxDiffPixelRatio: VISUAL_MAX_DIFF_PIXEL_RATIO,
          threshold: VISUAL_THRESHOLD,
          animations: "disabled",
          caret: "hide",
          scale: "css",
        },
      },
      metadata: { ...rest.metadata, composeService },
      globalSetup: join(HERE, "compose-up.ts"),
      globalTeardown: join(HERE, "compose-down.ts"),
    },
    env,
  );
  return { ...config, metadata: { ...config.metadata, composeService } };
}
