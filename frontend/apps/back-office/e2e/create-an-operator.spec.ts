import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";
import { screenshotName } from "@swarm/e2e";

import { OPERATOR_NAME, PLANNER_EMAIL, PLANNER_NAME, installSampleData } from "./sample-data.ts";
import type { SampleState } from "./sample-data.ts";

const USE_CASE = "UC-029";
const EXTENSION = ".png";
const OPERATOR_NAME_LABEL = "Operator name";
const JURISDICTION_LABEL = "EU (EASA)";
const NEXT_BUTTON = "Next: first Mission planner";
const PLANNER_NAME_LABEL = "Name";
const PLANNER_EMAIL_LABEL = "E-mail address";
const SUBMIT_BUTTON = "Create the Operator and send the invitation";
const TITLE_ENTRY = "Create an Operator";
const TITLE_PLANNER = "First Mission planner of Aerowing Services";
const BANNER_KO = "Operator not created.";
const BANNER_OK = "Aerowing Services created. Its data is isolated: no other Operator can see it.";
const TOAST_OK = `Invitation sent to ${PLANNER_EMAIL}.`;
const ENTRY_NODE = "a1";
const KO_NODE = "ko";
const PLANNER_NODE = "a2";
const OK_NODE = "ok";
const DIFFERENCE_TAG = "@difference";
const NO_UPDATE = "none";
const PATH_SEPARATOR = "/";
const NOTIFICATIONS_REGION = /Notifications/;

/**
 * The path segments of a screen: Playwright keeps an array of segments as it is, but turns every `/` and `.` of a
 * string name into `-`, which would miss `docs/specs/screens/UC-029/a1.dark.png`.
 */
function screen(node: string, project: string): string[] {
  return `${screenshotName(USE_CASE, node, project)}${EXTENSION}`.split(PATH_SEPARATOR);
}

async function open(page: Page, state: SampleState): Promise<void> {
  await installSampleData(page, state);
  await page.goto("/");
  await expect(page.getByRole("heading", { name: TITLE_ENTRY })).toBeVisible();
}

async function enterName(page: Page): Promise<void> {
  await page.getByLabel(OPERATOR_NAME_LABEL).fill(OPERATOR_NAME);
}

async function enterOperator(page: Page): Promise<void> {
  await enterName(page);
  await page.getByLabel(JURISDICTION_LABEL).check();
}

async function enterPlanner(page: Page): Promise<void> {
  await enterOperator(page);
  await page.getByRole("button", { name: NEXT_BUTTON }).click();
  await expect(page.getByRole("heading", { name: TITLE_PLANNER })).toBeVisible();
  await page.getByLabel(PLANNER_NAME_LABEL, { exact: true }).fill(PLANNER_NAME);
  await page.getByLabel(PLANNER_EMAIL_LABEL).fill(PLANNER_EMAIL);
}

test.describe("the Back office creates an Operator (UC-029)", () => {
  test("A1 Enter the Operator", async ({ page }, testInfo) => {
    await open(page, "a1");
    await enterOperator(page);
    await expect(page).toHaveScreenshot(screen(ENTRY_NODE, testInfo.project.name));
  });

  test("KO Operator not created", async ({ page }, testInfo) => {
    await open(page, "ko");
    await enterName(page);
    await page.getByRole("button", { name: NEXT_BUTTON }).click();
    await expect(page.getByText(BANNER_KO)).toBeVisible();
    await expect(page).toHaveScreenshot(screen(KO_NODE, testInfo.project.name));
  });

  test("A2 Invite the first Mission planner", async ({ page }, testInfo) => {
    await open(page, "a2");
    await enterPlanner(page);
    await expect(page).toHaveScreenshot(screen(PLANNER_NODE, testInfo.project.name));
  });

  test("OK Operator created and isolated", async ({ page }, testInfo) => {
    await open(page, "ok");
    await enterPlanner(page);
    await page.getByRole("button", { name: SUBMIT_BUTTON }).click();
    await expect(page.getByText(BANNER_OK)).toBeVisible();
    await expect(page.getByRole("region", { name: NOTIFICATIONS_REGION }).getByText(TOAST_OK)).toBeVisible();
    await expect(page).toHaveScreenshot(screen(OK_NODE, testInfo.project.name));
  });

  test("a large difference fails the build", { tag: DIFFERENCE_TAG }, async ({ page }, testInfo) => {
    test.skip(testInfo.config.updateSnapshots !== NO_UPDATE, "A capture must never overwrite the KO screen.");
    test.fail();
    await open(page, "a1");
    await enterOperator(page);
    await expect(page).toHaveScreenshot(screen(KO_NODE, testInfo.project.name));
  });
});
