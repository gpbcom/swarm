# QA

End-to-end tests that run against the real images of a pipeline run, never against a development server, so that they
test what ships.

| Path | Holds |
| --- | --- |
| [e2e/](e2e/) | `@swarm/e2e`, a package of the pnpm workspace |
| [e2e/src/define-e2e-config.ts](e2e/src/define-e2e-config.ts) | `defineE2eConfig`, the Playwright configuration every front end's end-to-end tests share |
| [e2e/e2e/images.spec.ts](e2e/e2e/images.spec.ts) | The suite that checks the images: every service of `infra/compose/e2e.yaml` is tagged with the image tag and never built, and the gateway's app imports and exits cleanly |
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
