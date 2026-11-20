import base from "@swarm/config/eslint";
import { defineConfig } from "eslint/config";

export default defineConfig({ ignores: ["src/generated/"] }, base, {
  languageOptions: {
    parserOptions: {
      projectService: true,
      tsconfigRootDir: import.meta.dirname,
    },
  },
}, {
  files: ["test/**/*.ts"],
  rules: { "@typescript-eslint/no-floating-promises": "off" },
});
