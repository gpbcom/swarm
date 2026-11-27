import { defineVisualConfig } from "@swarm/e2e";

export default defineVisualConfig({
  testDir: "./e2e",
  composeService: "back-office",
  use: { baseURL: "http://127.0.0.1:8181" },
});
