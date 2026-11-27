# T0.20: Review note

**Verdict:** ✅ Approved · **Branch:** `feature/tickets`

## What changed

- The visual tests are shared. `defineVisualConfig` in `@swarm/e2e` sets up a light and a dark project at the tokens' screen size (1280 x 800, scale 1, en-GB, UTC). It stores the screens in `docs/specs/screens`, never updates them by default and fails a screen when more than 2 % of its pixels differ beyond 0.2. It also starts and stops the front end's own compose service around the run.
- The Back office now has a real image (nginx-unprivileged on 8080, SPA fallback) and a compose service on `127.0.0.1:8181`. CI runs every front end's `e2e` against the images of the run.
- The UC-029 visual spec drives the real Back office through A1, KO, A2 and OK. Stubbed gateway and Keycloak answers supply the sample cast, and a `@difference` test proves that a large difference fails.
- The four UC-029 screens were captured from the app in both modes and palettised by the new `specs.py palettise`. Their rows are now `📸 Screenshot` and their mock-ups are deleted.
- At the person's word, the convention test asks for `capture` and `defineVisualConfig` only from front ends that compare screens. Ground control keeps the shared set-up.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given a Back office screen rendered with the sample data in light and dark mode, when it differs from its PNG by more than the allowed difference, then the build fails | `create-an-operator.spec.ts` › "a large difference fails the build" (`test.fail()` comparing A1 with KO), the qa/e2e unit tests of the tolerance in `tests-evidences/test.txt`, and `test_e2e_runs_the_front_ends_visual_tests` in `tests-evidences/pytest.txt` | ✅ Pass (no recorded Playwright run against the image, see follow-ups) |
| 2. Given A1, KO, A2 and OK of UC-029, when the ticket is done, then each is a 📸 Screenshot in light and dark mode at screen size and its mock-up is deleted | Eight PNGs, all 1280 x 800 palette PNGs that show the real Back office in the right state; four UC-029 rows set to 📸; four mock-ups deleted | ✅ Pass |
| 3. Given the screenshots in place, when `specs.py check` runs, then it prints nothing | `tests-evidences/specs-check.txt` (empty) | ✅ Pass |

## Look at first

- **How a screen name becomes a file:** `qa/e2e/src/define-visual-config.ts` (`screenshotName`, `snapshotPathTemplate`) and the `screen()` helper of `frontend/apps/back-office/e2e/create-an-operator.spec.ts`. The path is passed as segments so that Playwright does not mangle `a1.dark.png`.
- **The stubs stand in for identity:** `frontend/apps/back-office/e2e/sample-data.ts` answers the OIDC discovery, authorise and token endpoints with unsigned (`alg: none`) tokens that carry the `swarm_administrator` role. This is test-only code that ships in no image. Operator isolation is not exercised: only one Operator exists in the stub, and the KO state is a 409 on the taken name.
- **The compose lifecycle:** `qa/e2e/src/compose-up.ts` and `compose-down.ts`, together with the port test in `tests/ci/e2e/test_compose_e2e.py`. CI runs the Back office and Ground control suites side by side.
- **The capture guard:** the `capture` script in `frontend/apps/back-office/package.json` and the `test.skip` of the `@difference` test. A capture must never overwrite KO with A1.
- The image is `frontend/apps/back-office/Dockerfile`, which runs `apk upgrade` as root, then switches back to USER 101.

## Assumptions accepted

- The 2 % / 0.2 tolerance: accepted. It is decided in the plan as TICKET.md asked, and the unit tests pin it.
- Stubbed sample data with no backend: accepted. The image is real, and the cast comes from the visual identity.
- T0.20 builds the Back office image: accepted. T0.16 delivered none, and AGENT.md requires one image per front end.
- Port 127.0.0.1:8181: accepted. The person approved it, and a test keeps the host ports distinct.
- Visual convention checks only for front ends that compare screens: accepted. The person decided it.
- en-GB, UTC, scale 1, 1280 x 800: accepted, as the visual identity's screenshot rules say.
- BR-008 is linked, the link points to the S04 anchor and no budget is touched: accepted. All of it is derived from UC-029 and the roadmap.

## Follow-ups

- `images.yml` uploads the front-end reports twice. Keep one upload (K11, K05).
- The baselines were captured locally, and no e2e run output is in `tests-evidences/`. CI fonts may exceed 2 %: if so, recapture in CI (K13, K09).
- `qa/README.md` still says the front-end tests "will live in" `e2e/`, and AGENT.md still says the front-end Docker rules are untested (K12).
- In `test_frontend_e2e.py`, replace the `compress`/`map` chain with a readable comprehension (K06).
- The Dockerfile has a redundant `COPY` of the Back office `package.json` before `COPY frontend` (K10, K04).
- `test_palettise.py` keeps module-level constants and functions outside `helpers.py` (K02).
