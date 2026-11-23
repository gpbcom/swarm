import base from "@swarm/config/eslint";
import { defineConfig } from "eslint/config";

export default defineConfig({ ignores: ["src-tauri/", "dist/"] }, base, {
  languageOptions: {
    parserOptions: {
      projectService: true,
      tsconfigRootDir: import.meta.dirname,
    },
  },
});
