export { BROWSER_IMAGE, BROWSER_WS_ENDPOINT, PLAYWRIGHT_VERSION } from "./browser-server.ts";
export { defineE2eConfig } from "./define-e2e-config.ts";
export type { E2eEnvironment } from "./define-e2e-config.ts";
export {
  DARK_PROJECT,
  LIGHT_PROJECT,
  VISUAL_MAX_DIFF_PIXEL_RATIO,
  VISUAL_THRESHOLD,
  defineVisualConfig,
  screenshotName,
} from "./define-visual-config.ts";
export type { VisualConfig, VisualOptions } from "./define-visual-config.ts";
