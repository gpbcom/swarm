import { defineE2eConfig } from "@swarm/e2e";

const BASE_URL = "http://127.0.0.1:8180";
// Software WebGL, so that the map renders in a headless browser without a GPU.
const WEBGL_ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"];

export default defineE2eConfig({
  testDir: "./e2e",
  globalSetup: "./e2e/global-setup.ts",
  use: { baseURL: BASE_URL, launchOptions: { args: WEBGL_ARGS } },
});
