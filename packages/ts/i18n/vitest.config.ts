import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    projects: [
      { test: { name: "node", environment: "node", include: ["test/**/*.test.ts"] } },
      { test: { name: "dom", environment: "jsdom", globals: true, include: ["test/**/*.test.tsx"] } },
    ],
  },
});
