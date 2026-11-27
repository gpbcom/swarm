import base from "@swarm/config/eslint";
import { defineConfig } from "eslint/config";

export default defineConfig(base, {
  languageOptions: {
    parserOptions: {
      projectService: true,
      tsconfigRootDir: import.meta.dirname,
    },
  },
}, {
  files: ["test/**/*.ts"],
  rules: {
    "@typescript-eslint/no-floating-promises": "off",
    "@typescript-eslint/no-unnecessary-condition": "off",
    "@typescript-eslint/array-type": "off",
  },
});
