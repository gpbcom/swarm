import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { defineE2eConfig } from "../src/define-e2e-config.ts";

const TEST_DIR = "e2e";
const TAG_VARIABLE = "SWARM_IMAGE_TAG";
const BASE_URL_VARIABLE = "SWARM_E2E_BASE_URL";
const HTML_REPORTER: [string, { outputFolder: string; open: string }] = [
  "html",
  { outputFolder: "playwright-report", open: "never" },
];

function assertErrorMatching(action: () => unknown, pattern: RegExp): void {
  assert.throws(action, (error: Error) => {
    assert.ok(error instanceof Error);
    assert.match(error.message, pattern);
    return true;
  });
}

describe("the shared Playwright configuration", () => {
  it("keeps the test folder, has no web server and writes an html report", () => {
    const config = defineE2eConfig({ testDir: TEST_DIR }, { [TAG_VARIABLE]: "abc123" });
    assert.equal(config.testDir, TEST_DIR);
    assert.equal(config.webServer, undefined);
    assert.deepEqual(config.reporter, [HTML_REPORTER]);
  });

  it("uses the base URL of the environment when it is set", () => {
    const config = defineE2eConfig(
      { testDir: TEST_DIR },
      { [TAG_VARIABLE]: "abc123", [BASE_URL_VARIABLE]: "http://localhost:8080" },
    );
    assert.equal(config.use?.baseURL, "http://localhost:8080");
  });

  it("has no base URL when the environment has none", () => {
    const config = defineE2eConfig({ testDir: TEST_DIR }, { [TAG_VARIABLE]: "abc123" });
    assert.equal(config.use?.baseURL, undefined);
  });

  it("refuses a missing image tag", () => {
    assertErrorMatching(() => defineE2eConfig({ testDir: TEST_DIR }, {}), new RegExp(TAG_VARIABLE));
  });

  it("refuses a blank image tag", () => {
    assertErrorMatching(
      () => defineE2eConfig({ testDir: TEST_DIR }, { [TAG_VARIABLE]: "   " }),
      new RegExp(TAG_VARIABLE),
    );
  });

  it("refuses a development server", () => {
    const options = { testDir: TEST_DIR, webServer: { command: "npm run dev" } };
    assertErrorMatching(() => defineE2eConfig(options, { [TAG_VARIABLE]: "abc123" }), /development server/i);
  });

  it("forbids test.only on CI", () => {
    const config = defineE2eConfig({ testDir: TEST_DIR }, { [TAG_VARIABLE]: "abc123", CI: "true" });
    assert.equal(config.forbidOnly, true);
  });
});
