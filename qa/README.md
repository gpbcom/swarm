# QA

End-to-end tests that run against the real images of a pipeline run, never against a development server, so that they
test what ships.

| Path | Holds |
| --- | --- |
| [e2e/](e2e/) | `@swarm/e2e`, a package of the pnpm workspace |
| [e2e/src/define-e2e-config.ts](e2e/src/define-e2e-config.ts) | `defineE2eConfig`, the Playwright configuration every front end's end-to-end tests share |
| [e2e/e2e/images.spec.ts](e2e/e2e/images.spec.ts) | The suite that checks the images: every service of `infra/compose/e2e.yaml` is tagged with the image tag and never built, and the gateway's app imports and exits cleanly |
| [e2e/src/define-visual-config.ts](e2e/src/define-visual-config.ts) | `defineVisualConfig`, the configuration of the visual tests: a light and a dark project, the screen size from the tokens, and the screens stored in `docs/specs/screens` |
| [e2e/src/compose-up.ts](e2e/src/compose-up.ts) | Starts the compose service of a front end's tests, from `infra/compose/e2e.yaml`, before they run |
| [e2e/src/compose-down.ts](e2e/src/compose-down.ts) | Stops that compose service once the tests are done |
| [e2e/test/](e2e/test/) | The unit tests of the configuration, run with Node's test runner |

`defineE2eConfig` refuses to run without `SWARM_IMAGE_TAG`, the tag of the images under test, and refuses a
`webServer`. `SWARM_E2E_BASE_URL`, when set, is the base URL of the tests. The HTML report is written to
`e2e/playwright-report/`.

## Run it

From the repository root, with Docker, against images already pushed or built under that tag:

```bash
SWARM_IMAGE_TAG=<tag> pnpm --filter ./qa/e2e run e2e
```

`infra/compose/e2e.yaml` starts the images from `${SWARM_IMAGE_REGISTRY:-ghcr.io/gpbcom/swarm}/<name>:<tag>`. The
package's other scripts are `lint`, `typecheck` and `test`:

```bash
pnpm --filter ./qa/e2e test
```

In CI, the `e2e` job of `.github/workflows/images.yml` runs this suite after the images are built, scanned, pushed and
signed, and uploads the HTML report when a test fails. The front ends' own Playwright tests will live in
`frontend/apps/<frontend>/e2e/` and use the same configuration.

## Visual tests and the capture of screens

`defineVisualConfig` builds, for a front end, the Playwright configuration that compares each screen with its PNG of
the specification (SPEC-12). It declares two projects, `light` and `dark`, which set `colorScheme` to match. The
viewport is the screen size of the visual identity, read from `frontend/packages/tokens/src/tokens.css`, with a device
scale of 1, the locale `en-GB` and the time zone `UTC`. `snapshotPathTemplate` points into `docs/specs/screens`, so a
screen is stored beside its use case. A screen fails when more than 2 % of its pixels (`maxDiffPixelRatio` 0.02) differ
beyond a per-pixel threshold of 0.2. Animations and the caret are disabled, so that two runs match.

`screenshotName(useCase, node, project)` gives the name of a screen relative to `docs/specs/screens`: `UC-029/a1` for
the light project and `UC-029/a1.dark` for the dark one. The file names are those of SPEC-12. Give it to
`toHaveScreenshot` as path segments (`UC-029`, `a1.dark.png`): Playwright turns every `/` and `.` of a single
string name into `-`.

A front end's Playwright set-up starts its own compose service, named by `composeService`, through `compose-up.ts`,
and stops it through `compose-down.ts`. The tests therefore run against the real image, never a development server.

Build the image of the Back office, then run its tests against it from the repository root:

```bash
docker build -f frontend/apps/back-office/Dockerfile -t ghcr.io/gpbcom/swarm/back-office:local .
SWARM_IMAGE_TAG=local pnpm --filter @swarm/back-office run e2e
```

The Back office is published on `127.0.0.1:8181` and Ground control on `8180`, so that CI runs both suites at once.

To capture the screens, that is to replace the mock-up of a state with what the application shows, run the `capture`
script, which rewrites every screen with `--update-snapshots=all` and skips the tests tagged `@difference`. Then turn
the captures into 256-colour palette PNGs for the use case:

```bash
SWARM_IMAGE_TAG=local pnpm --filter @swarm/back-office run capture
python3 .claude/skills/write-specs/scripts/specs.py palettise UC-029
```

The screen row of the use case then takes the source `📸 Screenshot`, and its mock-up is deleted (SPEC-12).

In CI, the `e2e` job of `.github/workflows/images.yml` runs `pnpm --filter "./frontend/apps/*" --if-present run e2e`
after the suite of `qa/e2e`, so the visual tests of every front end run against the images of the pipeline.
