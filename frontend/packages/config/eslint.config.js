import eslint from "@eslint/js";
import { defineConfig } from "eslint/config";
import tseslint from "typescript-eslint";

const TEST_FILES = ["src/**/*.test.{ts,tsx}", "src/**/*.spec.{ts,tsx}"];

/**
 * @param {string[]} group
 * @param {string} message
 * @param {string[]} regex
 * @returns {{ "no-restricted-imports": ["error", { patterns: ({ group: string[]; message: string } | { regex: string; message: string })[] }] }}
 */
const boundary = (group, message, regex = []) => ({
  "no-restricted-imports": [
    "error",
    {
      patterns: [
        { group, message },
        ...regex.map((item) => ({ regex: item, message })),
      ],
    },
  ],
});

const FEATURE_MESSAGE =
  "A feature never imports another feature, the app shell or the testing helpers. Share through src/stores or @swarm/*.";
const FEATURE_ALIASED = [
  "**/features/*",
  "**/features/*/**",
  "**/app",
  "**/app/**",
  "**/testing",
  "**/testing/**",
];
const FEATURE_MAX_DEPTH = 6;

// A relative import cannot be told apart from an import inside the feature by its text alone, so each folder depth
// of a feature forbids the one climb that lands in src/features/, where the sibling features are.
const featureBlocks = Array.from({ length: FEATURE_MAX_DEPTH }, (_, index) => {
  const depth = index + 1;
  return {
    files: [`src/features/*/${"*/".repeat(depth - 1)}*.{ts,tsx}`],
    ignores: TEST_FILES,
    rules: boundary(FEATURE_ALIASED, FEATURE_MESSAGE, [
      `^(\\.\\./){${String(depth)}}[^./]`,
    ]),
  };
});

export default defineConfig(
  { ignores: ["dist/", "node_modules/"] },
  eslint.configs.recommended,
  tseslint.configs.strictTypeChecked,
  tseslint.configs.stylisticTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
  ...featureBlocks,
  {
    files: ["src/stores/**/*.{ts,tsx}"],
    ignores: TEST_FILES,
    rules: boundary(
      [
        "**/features",
        "**/features/**",
        "**/app",
        "**/app/**",
        "**/testing",
        "**/testing/**",
      ],
      "A store never imports a feature, the app shell or the testing helpers.",
    ),
  },
  {
    files: ["src/app/**/*.{ts,tsx}", "src/*.{ts,tsx}"],
    ignores: TEST_FILES,
    rules: boundary(
      ["**/testing", "**/testing/**"],
      "The testing helpers are imported by tests only.",
    ),
  },
);
