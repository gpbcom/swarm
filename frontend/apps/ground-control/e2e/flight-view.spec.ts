import { expect, test } from "@playwright/test";

import { LiveStandInServer } from "./live-stand-in-server.js";

const MISSION_ID = "01930000-0000-7000-8000-000000000001";
const DRONE_COUNT = "10";
const MOVE_WAIT_MS = 1_000;
const MAP_LABEL = "Map of the Squad";
const FLIGHT_MAP = "section.flight-map";
const COUNT_ATTRIBUTE = "data-drone-count";

let server: LiveStandInServer;

test.beforeEach(async ({ page }) => {
  server = await LiveStandInServer.start(MISSION_ID);
  await page.route("**/config.json", (route) =>
    route.fulfill({
      json: {
        liveUrl: `ws://127.0.0.1:${String(server.port)}/v1/live`,
        missionId: MISSION_ID,
        tilesUrl: "tiles/basemap.pmtiles",
        metricsUrl: null,
        metricsIntervalS: 60,
        cell: null,
        livePath: "edge",
      },
    }),
  );
  await page.route("**/tiles/**", (route) => route.fulfill({ status: 404 }));
});

test.afterEach(async () => {
  await server.stop();
});

test.describe("the flight view of Ground control", () => {
  test("shows the fixed safety controls in the title bar", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("button", { name: /Hold the Squad/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /Abort/ })).toBeVisible();
  });

  test("shows the ten Drones of the Squad on the map", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("region", { name: MAP_LABEL })).toBeVisible();
    await expect(page.locator(FLIGHT_MAP)).toHaveAttribute(COUNT_ATTRIBUTE, DRONE_COUNT);
  });

  test("moves the Drones: two screenshots one second apart differ", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator(FLIGHT_MAP)).toHaveAttribute(COUNT_ATTRIBUTE, DRONE_COUNT);
    const map = page.getByRole("region", { name: MAP_LABEL });
    const before = await map.screenshot();
    await page.waitForTimeout(MOVE_WAIT_MS);
    const after = await map.screenshot();
    expect(before.equals(after)).toBe(false);
  });

  test("sends nothing but the subscription when Hold and Abort are clicked", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator(FLIGHT_MAP)).toHaveAttribute(COUNT_ATTRIBUTE, DRONE_COUNT);
    await page.getByRole("button", { name: /Hold the Squad/ }).click();
    await page.getByRole("button", { name: /Abort/ }).click();
    expect(server.received).toHaveLength(1);
    expect(server.received[0]).toMatchObject({
      op: "subscribe",
      topic: `mission/${MISSION_ID}/squad`,
      rate: "full",
    });
  });
});
