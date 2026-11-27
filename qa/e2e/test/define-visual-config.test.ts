import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

import {
  BROWSER_IMAGE,
  BROWSER_WS_ENDPOINT,
  DARK_PROJECT,
  LIGHT_PROJECT,
  PLAYWRIGHT_VERSION,
  VISUAL_MAX_DIFF_PIXEL_RATIO,
  VISUAL_THRESHOLD,
  defineVisualConfig,
  screenshotName,
} from "../src/index.ts";

const TEST_DIR = "e2e";
const SERVICE = "ground-control";
const TAG_VARIABLE = "SWARM_IMAGE_TAG";
const BASE_URL_VARIABLE = "SWARM_E2E_BASE_URL";
const ENVIRONMENT = { [TAG_VARIABLE]: "abc123" };
const OPTIONS = { testDir: TEST_DIR, composeService: SERVICE };
const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPOSITORY_ROOT = path.resolve(HERE, "../../..");
const TOKENS_FILE = path.join(REPOSITORY_ROOT, "frontend/packages/tokens/src/tokens.css");
const SHARED_PACKAGE = path.join(REPOSITORY_ROOT, "qa/e2e/package.json");

function token(name: string): number {
  const match = new RegExp(`--${name}:\\s*(\\d+)px`).exec(readFileSync(TOKENS_FILE, "utf-8"));
  assert.ok(match, `token ${name} is missing`);
  return Number(match[1]);
}

function projectNamed(name: string) {
  const config = defineVisualConfig(OPTIONS, ENVIRONMENT);
  const project = config.projects?.find((candidate) => candidate.name === name);
  assert.ok(project, `project ${name} is missing`);
  return project;
}

describe("the shared visual Playwright configuration", () => {
  it("refuses a missing image tag", () => {
    assert.throws(() => defineVisualConfig(OPTIONS, {}), new RegExp(TAG_VARIABLE));
  });

  it("refuses a development server", () => {
    const options = { ...OPTIONS, webServer: { command: "npm run dev" } };
    assert.throws(() => defineVisualConfig(options, ENVIRONMENT), /development server/i);
  });

  it("has a light and a dark project and nothing else", () => {
    const config = defineVisualConfig(OPTIONS, ENVIRONMENT);
    assert.deepEqual(
      config.projects?.map((project) => project.name),
      [LIGHT_PROJECT, DARK_PROJECT],
    );
    assert.equal(projectNamed(LIGHT_PROJECT).use?.colorScheme, "light");
    assert.equal(projectNamed(DARK_PROJECT).use?.colorScheme, "dark");
  });

  it("names the two projects light and dark", () => {
    assert.equal(LIGHT_PROJECT, "light");
    assert.equal(DARK_PROJECT, "dark");
  });

  for (const name of ["light", "dark"]) {
    it(`renders the ${name} project at the screen size of the tokens`, () => {
      const use = projectNamed(name).use;
      assert.deepEqual(use?.viewport, { width: token("screen-width"), height: token("screen-height") });
    });

    it(`fixes the scale, the locale and the time zone of the ${name} project`, () => {
      const use = projectNamed(name).use;
      assert.equal(use?.deviceScaleFactor, 1);
      assert.equal(use.locale, "en-GB");
      assert.equal(use.timezoneId, "UTC");
    });
  }

  it("stores the screens in the specification folder", () => {
    const config = defineVisualConfig(OPTIONS, ENVIRONMENT);
    const template = path.join(REPOSITORY_ROOT, "docs/specs/screens", "{arg}{ext}");
    assert.equal(config.snapshotPathTemplate, template);
    assert.ok(path.isAbsolute(config.snapshotPathTemplate ?? ""));
  });

  it("never updates the screens of the specification", () => {
    assert.equal(defineVisualConfig(OPTIONS, ENVIRONMENT).updateSnapshots, "none");
  });

  it("compares screenshots with the shared tolerance", () => {
    const options = defineVisualConfig(OPTIONS, ENVIRONMENT).expect?.toHaveScreenshot;
    assert.equal(options?.maxDiffPixelRatio, VISUAL_MAX_DIFF_PIXEL_RATIO);
    assert.equal(options.threshold, VISUAL_THRESHOLD);
    assert.equal(options.animations, "disabled");
    assert.equal(options.caret, "hide");
    assert.equal(options.scale, "css");
  });

  it("states the tolerance constants", () => {
    assert.equal(VISUAL_MAX_DIFF_PIXEL_RATIO, 0.02);
    assert.equal(VISUAL_THRESHOLD, 0.2);
  });

  it("records the compose service in the metadata", () => {
    assert.equal(defineVisualConfig(OPTIONS, ENVIRONMENT).metadata.composeService, SERVICE);
  });

  it("starts and stops the compose stack with existing files", () => {
    const config = defineVisualConfig(OPTIONS, ENVIRONMENT);
    for (const [value, file] of [
      [config.globalSetup, "compose-up.ts"],
      [config.globalTeardown, "compose-down.ts"],
    ] as const) {
      assert.equal(typeof value, "string");
      assert.ok(path.isAbsolute(value as string));
      assert.equal(path.basename(value as string), file);
      assert.ok(existsSync(value as string));
    }
  });

  for (const name of ["light", "dark"]) {
    it(`renders the ${name} project in the browser of the pinned Playwright image`, () => {
      assert.deepEqual(projectNamed(name).use?.connectOptions, { wsEndpoint: BROWSER_WS_ENDPOINT });
    });
  }

  it("pins the browser image to the Playwright version of the shared set-up", () => {
    const shared = JSON.parse(readFileSync(SHARED_PACKAGE, "utf-8")) as { devDependencies: Record<string, string> };
    assert.equal(PLAYWRIGHT_VERSION, shared.devDependencies["@playwright/test"]);
    assert.equal(BROWSER_IMAGE, `mcr.microsoft.com/playwright:v${PLAYWRIGHT_VERSION}-noble`);
  });

  it("reaches the browser server on the loopback", () => {
    assert.match(BROWSER_WS_ENDPOINT, /^ws:\/\/127\.0\.0\.1:\d+\/$/);
  });

  it("uses the base URL of the environment when it is set", () => {
    const config = defineVisualConfig(OPTIONS, { ...ENVIRONMENT, [BASE_URL_VARIABLE]: "http://localhost:8080" });
    assert.equal(config.use?.baseURL, "http://localhost:8080");
  });

  it("has no base URL when the environment has none", () => {
    assert.equal(defineVisualConfig(OPTIONS, ENVIRONMENT).use?.baseURL, undefined);
  });
});

describe("the name of a screenshot", () => {
  it("is the use case and the node in light mode", () => {
    assert.equal(screenshotName("UC-029", "a1", LIGHT_PROJECT), "UC-029/a1");
  });

  it("ends with dark in dark mode", () => {
    assert.equal(screenshotName("UC-029", "a1", DARK_PROJECT), "UC-029/a1.dark");
  });

  it("refuses another project name", () => {
    assert.throws(() => screenshotName("UC-029", "a1", "mobile"), Error);
  });
});
