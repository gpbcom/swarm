# T0.20: Visual tests and UC-029 screenshots

**Status:** ✅ Done · **Ticket:** [TICKET.md](TICKET.md) · **Choices and trade-offs:** [IMPLEMENTATION.md](IMPLEMENTATION.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🔭 What it does

- Every front end that compares screens gets one shared Playwright set-up: a light and a dark project at the screen size of the tokens, screens stored beside their use case, and a build that fails when a screen differs by more than 2 % of its pixels.
- The Back office now has a real image and a compose service, and a visual spec drives it through the four screens of UC-029.
- The four UC-029 screens (A1, KO, A2, OK) are captured from the running app in light and dark mode, are 📸 Screenshot, and their mock-ups are deleted.
- A new `specs.py palettise` command turns captured screenshots into 256-colour palette PNGs, as SPEC-12 asks.

## ⚙️ How it works

1. **The image is built:** the Back office is built with pnpm in a Node stage, then served by unprivileged nginx on 8080 after an `apk upgrade`, in [`frontend/apps/back-office/Dockerfile:1-19`](../../../frontend/apps/back-office/Dockerfile#L1-L19). nginx falls back to `index.html` for the single-page app in [`frontend/apps/back-office/nginx.conf:11-14`](../../../frontend/apps/back-office/nginx.conf#L11-L14).
2. **Compose publishes it:** the `back-office` service maps `127.0.0.1:8181` to 8080 (Ground control holds 8180), in [`infra/compose/e2e.yaml:14-19`](../../../infra/compose/e2e.yaml#L14-L19).
3. **The front end declares its config:** [`frontend/apps/back-office/playwright.config.ts:3-7`](../../../frontend/apps/back-office/playwright.config.ts#L3-L7) calls `defineVisualConfig` with its compose service and base URL.
4. **The shared config is built:** `defineVisualConfig` reads the screen size from the tokens ([`qa/e2e/src/define-visual-config.ts:60-61`](../../../qa/e2e/src/define-visual-config.ts#L60-L61)), adds the light and dark projects at scale 1, `en-GB` and `UTC` ([`qa/e2e/src/define-visual-config.ts:62-69`](../../../qa/e2e/src/define-visual-config.ts#L62-L69)), points snapshots into `docs/specs/screens` and never updates them by default ([`qa/e2e/src/define-visual-config.ts:70-71`](../../../qa/e2e/src/define-visual-config.ts#L70-L71)), and sets the tolerance ([`qa/e2e/src/define-visual-config.ts:72-80`](../../../qa/e2e/src/define-visual-config.ts#L72-L80)).
5. **The stack starts and stops around the run:** `globalSetup` runs `docker compose up -d` for the service, then polls the base URL until it answers 200 ([`qa/e2e/src/compose-up.ts:18-48`](../../../qa/e2e/src/compose-up.ts#L18-L48)). `globalTeardown` removes the service ([`qa/e2e/src/compose-down.ts:14-27`](../../../qa/e2e/src/compose-down.ts#L14-L27)).
6. **Sample data stands in for the backend:** `installSampleData` stubs the identity provider and the gateway with the visual identity's cast, Aerowing Services and Léa Martin ([`frontend/apps/back-office/e2e/sample-data.ts:153-158`](../../../frontend/apps/back-office/e2e/sample-data.ts#L153-L158)). The tokens are unsigned (`alg: none`, [`frontend/apps/back-office/e2e/sample-data.ts:88`](../../../frontend/apps/back-office/e2e/sample-data.ts#L88)).
7. **Each screen is driven and compared:** A1, KO, A2 and OK fill the form and call `toHaveScreenshot` ([`frontend/apps/back-office/e2e/create-an-operator.spec.ts:62-89`](../../../frontend/apps/back-office/e2e/create-an-operator.spec.ts#L62-L89)). The file name comes from `screen()`, which gives path segments so that `a1.dark.png` is not mangled ([`frontend/apps/back-office/e2e/create-an-operator.spec.ts:34-36`](../../../frontend/apps/back-office/e2e/create-an-operator.spec.ts#L34-L36)) and from `screenshotName` ([`qa/e2e/src/define-visual-config.ts:41-49`](../../../qa/e2e/src/define-visual-config.ts#L41-L49)).
8. **A large difference is proved to fail:** the `@difference` test compares A1 with the KO PNG under `test.fail()`, and is skipped during a capture ([`frontend/apps/back-office/e2e/create-an-operator.spec.ts:91-97`](../../../frontend/apps/back-office/e2e/create-an-operator.spec.ts#L91-L97)).
9. **Screens are captured:** `pnpm run capture` runs `--update-snapshots=all --grep-invert @difference` ([`frontend/apps/back-office/package.json:10-11`](../../../frontend/apps/back-office/package.json#L10-L11)), then `specs.py palettise UC-029` turns the RGB files into palette PNGs ([`.claude/skills/write-specs/scripts/specs.py:129-141`](../../../.claude/skills/write-specs/scripts/specs.py#L129-L141)).
10. **CI runs it:** the `e2e` job runs every front end's `e2e` script against the run's images ([`.github/workflows/images.yml:168-170`](../../../.github/workflows/images.yml#L168-L170)).

## 🧱 Files and lines changed

<!-- changes -->
| File | Change | Lines in the new version | Added | Removed |
| --- | --- | --- | --- | --- |
| [`.claude/rules/enforcement.json`](../../../.claude/rules/enforcement.json) | Modified | [166-175](../../../.claude/rules/enforcement.json#L166), [188-192](../../../.claude/rules/enforcement.json#L188) | +15 | −0 |
| [`.claude/skills/write-specs/SKILL.md`](../../../.claude/skills/write-specs/SKILL.md) | Modified | [25](../../../.claude/skills/write-specs/SKILL.md#L25) | +1 | −0 |
| [`.claude/skills/write-specs/scripts/spec_check.py`](../../../.claude/skills/write-specs/scripts/spec_check.py) | Modified | [363](../../../.claude/skills/write-specs/scripts/spec_check.py#L363) | +1 | −1 |
| [`.claude/skills/write-specs/scripts/specs.py`](../../../.claude/skills/write-specs/scripts/specs.py) | Modified | [14-15](../../../.claude/skills/write-specs/scripts/specs.py#L14), [24](../../../.claude/skills/write-specs/scripts/specs.py#L24), [32](../../../.claude/skills/write-specs/scripts/specs.py#L32), [129-143](../../../.claude/skills/write-specs/scripts/specs.py#L129), [178-179](../../../.claude/skills/write-specs/scripts/specs.py#L178) | +21 | −1 |
| [`.github/workflows/images.yml`](../../../.github/workflows/images.yml) | Modified | [168](../../../.github/workflows/images.yml#L168), [178-183](../../../.github/workflows/images.yml#L178) | +7 | −1 |
| [`AGENT.md`](../../../AGENT.md) | Modified | [61-68](../../../AGENT.md#L61), [390-391](../../../AGENT.md#L390) | +10 | −0 |
| [`docs/specs/functional/use-cases/UC-029-create-an-operator.md`](../../../docs/specs/functional/use-cases/UC-029-create-an-operator.md) | Modified | [7](../../../docs/specs/functional/use-cases/UC-029-create-an-operator.md#L7), [95-98](../../../docs/specs/functional/use-cases/UC-029-create-an-operator.md#L95) | +5 | −5 |
| [`docs/specs/screens/UC-029/a1.dark.png`](../../../docs/specs/screens/UC-029/a1.dark.png) | Modified | binary | +- | −- |
| [`docs/specs/screens/UC-029/a1.png`](../../../docs/specs/screens/UC-029/a1.png) | Modified | binary | +- | −- |
| [`docs/specs/screens/UC-029/a2.dark.png`](../../../docs/specs/screens/UC-029/a2.dark.png) | Modified | binary | +- | −- |
| [`docs/specs/screens/UC-029/a2.png`](../../../docs/specs/screens/UC-029/a2.png) | Modified | binary | +- | −- |
| [`docs/specs/screens/UC-029/ko.dark.png`](../../../docs/specs/screens/UC-029/ko.dark.png) | Modified | binary | +- | −- |
| [`docs/specs/screens/UC-029/ko.png`](../../../docs/specs/screens/UC-029/ko.png) | Modified | binary | +- | −- |
| [`docs/specs/screens/UC-029/ok.dark.png`](../../../docs/specs/screens/UC-029/ok.dark.png) | Modified | binary | +- | −- |
| [`docs/specs/screens/UC-029/ok.png`](../../../docs/specs/screens/UC-029/ok.png) | Modified | binary | +- | −- |
| `docs/specs/screens/mockups/UC-029/a1.html` | Deleted | ➖ deleted | +0 | −44 |
| `docs/specs/screens/mockups/UC-029/a2.html` | Deleted | ➖ deleted | +0 | −44 |
| `docs/specs/screens/mockups/UC-029/ko.html` | Deleted | ➖ deleted | +0 | −46 |
| `docs/specs/screens/mockups/UC-029/ok.html` | Deleted | ➖ deleted | +0 | −34 |
| [`frontend/apps/back-office/Dockerfile`](../../../frontend/apps/back-office/Dockerfile) | Added | [1-19](../../../frontend/apps/back-office/Dockerfile#L1) | +19 | −0 |
| [`frontend/apps/back-office/e2e/create-an-operator.spec.ts`](../../../frontend/apps/back-office/e2e/create-an-operator.spec.ts) | Added | [1-98](../../../frontend/apps/back-office/e2e/create-an-operator.spec.ts#L1) | +98 | −0 |
| [`frontend/apps/back-office/e2e/sample-data.ts`](../../../frontend/apps/back-office/e2e/sample-data.ts) | Added | [1-205](../../../frontend/apps/back-office/e2e/sample-data.ts#L1) | +205 | −0 |
| [`frontend/apps/back-office/eslint.config.js`](../../../frontend/apps/back-office/eslint.config.js) | Modified | [4](../../../frontend/apps/back-office/eslint.config.js#L4) | +1 | −1 |
| [`frontend/apps/back-office/nginx.conf`](../../../frontend/apps/back-office/nginx.conf) | Added | [1-15](../../../frontend/apps/back-office/nginx.conf#L1) | +15 | −0 |
| [`frontend/apps/back-office/package.json`](../../../frontend/apps/back-office/package.json) | Modified | [9-11](../../../frontend/apps/back-office/package.json#L9), [26](../../../frontend/apps/back-office/package.json#L26), [28](../../../frontend/apps/back-office/package.json#L28) | +5 | −1 |
| [`frontend/apps/back-office/playwright.config.ts`](../../../frontend/apps/back-office/playwright.config.ts) | Added | [1-7](../../../frontend/apps/back-office/playwright.config.ts#L1) | +7 | −0 |
| [`frontend/apps/back-office/tsconfig.json`](../../../frontend/apps/back-office/tsconfig.json) | Modified | [22](../../../frontend/apps/back-office/tsconfig.json#L22), [24-25](../../../frontend/apps/back-office/tsconfig.json#L24) | +3 | −1 |
| [`infra/compose/e2e.yaml`](../../../infra/compose/e2e.yaml) | Modified | [14-19](../../../infra/compose/e2e.yaml#L14) | +6 | −0 |
| [`pnpm-lock.yaml`](../../../pnpm-lock.yaml) | Modified | [215-217](../../../pnpm-lock.yaml#L215), [221-223](../../../pnpm-lock.yaml#L221) | +6 | −0 |
| [`qa/README.md`](../../../qa/README.md) | Modified | [11-13](../../../qa/README.md#L11), [38-77](../../../qa/README.md#L38) | +43 | −0 |
| [`qa/e2e/src/compose-down.ts`](../../../qa/e2e/src/compose-down.ts) | Added | [1-27](../../../qa/e2e/src/compose-down.ts#L1) | +27 | −0 |
| [`qa/e2e/src/compose-up.ts`](../../../qa/e2e/src/compose-up.ts) | Added | [1-49](../../../qa/e2e/src/compose-up.ts#L1) | +49 | −0 |
| [`qa/e2e/src/define-visual-config.ts`](../../../qa/e2e/src/define-visual-config.ts) | Added | [1-88](../../../qa/e2e/src/define-visual-config.ts#L1) | +88 | −0 |
| [`qa/e2e/src/index.ts`](../../../qa/e2e/src/index.ts) | Modified | [3-11](../../../qa/e2e/src/index.ts#L3) | +9 | −0 |
| [`qa/e2e/test/define-visual-config.test.ts`](../../../qa/e2e/test/define-visual-config.test.ts) | Added | [1-142](../../../qa/e2e/test/define-visual-config.test.ts#L1) | +142 | −0 |
| [`tests/ci/e2e/test_compose_e2e.py`](../../../tests/ci/e2e/test_compose_e2e.py) | Modified | [28-30](../../../tests/ci/e2e/test_compose_e2e.py#L28), [98-111](../../../tests/ci/e2e/test_compose_e2e.py#L98) | +17 | −0 |
| [`tests/ci/images/test_images_workflow.py`](../../../tests/ci/images/test_images_workflow.py) | Modified | [22-24](../../../tests/ci/images/test_images_workflow.py#L22), [77-80](../../../tests/ci/images/test_images_workflow.py#L77), [225-248](../../../tests/ci/images/test_images_workflow.py#L225) | +31 | −3 |
| [`tests/conventions/mono_repo/frontend/test_frontend_e2e.py`](../../../tests/conventions/mono_repo/frontend/test_frontend_e2e.py) | Added | [1-121](../../../tests/conventions/mono_repo/frontend/test_frontend_e2e.py#L1) | +121 | −0 |
| [`tests/harness/write_specs/helpers.py`](../../../tests/harness/write_specs/helpers.py) | Modified | [20](../../../tests/harness/write_specs/helpers.py#L20), [35-36](../../../tests/harness/write_specs/helpers.py#L35), [38](../../../tests/harness/write_specs/helpers.py#L38) | +4 | −3 |
| [`tests/harness/write_specs/test_palettise.py`](../../../tests/harness/write_specs/test_palettise.py) | Added | [1-115](../../../tests/harness/write_specs/test_palettise.py#L1) | +115 | −0 |
| [`tests/infra/images/test_back_office_image.py`](../../../tests/infra/images/test_back_office_image.py) | Added | [1-83](../../../tests/infra/images/test_back_office_image.py#L1) | +83 | −0 |
| **41 files** | | | **+1154** | **−185** |
<!-- /changes -->

- [`qa/e2e/src/define-visual-config.ts`](../../../qa/e2e/src/define-visual-config.ts), [`qa/e2e/src/compose-up.ts`](../../../qa/e2e/src/compose-up.ts), [`qa/e2e/src/compose-down.ts`](../../../qa/e2e/src/compose-down.ts), [`qa/e2e/src/index.ts`](../../../qa/e2e/src/index.ts): the shared visual set-up and its compose lifecycle, exported for front ends. [`qa/e2e/test/define-visual-config.test.ts`](../../../qa/e2e/test/define-visual-config.test.ts) pins the projects, the tolerance and the names.
- [`frontend/apps/back-office/Dockerfile`](../../../frontend/apps/back-office/Dockerfile), [`frontend/apps/back-office/nginx.conf`](../../../frontend/apps/back-office/nginx.conf): the missing Back office image. [`tests/infra/images/test_back_office_image.py`](../../../tests/infra/images/test_back_office_image.py) checks it.
- [`frontend/apps/back-office/e2e/create-an-operator.spec.ts`](../../../frontend/apps/back-office/e2e/create-an-operator.spec.ts), [`frontend/apps/back-office/e2e/sample-data.ts`](../../../frontend/apps/back-office/e2e/sample-data.ts), [`frontend/apps/back-office/playwright.config.ts`](../../../frontend/apps/back-office/playwright.config.ts): the UC-029 visual spec, its stubs and its config.
- [`frontend/apps/back-office/package.json`](../../../frontend/apps/back-office/package.json), [`frontend/apps/back-office/tsconfig.json`](../../../frontend/apps/back-office/tsconfig.json), [`frontend/apps/back-office/eslint.config.js`](../../../frontend/apps/back-office/eslint.config.js), [`pnpm-lock.yaml`](../../../pnpm-lock.yaml): the `e2e` and `capture` scripts, Playwright and `@swarm/e2e` as dev dependencies, and the e2e files in the type check and lint.
- [`infra/compose/e2e.yaml`](../../../infra/compose/e2e.yaml), [`tests/ci/e2e/test_compose_e2e.py`](../../../tests/ci/e2e/test_compose_e2e.py): the service on 8181, and the test that host ports stay distinct ([`tests/ci/e2e/test_compose_e2e.py:106`](../../../tests/ci/e2e/test_compose_e2e.py#L106)).
- [`.github/workflows/images.yml`](../../../.github/workflows/images.yml), [`tests/ci/images/test_images_workflow.py`](../../../tests/ci/images/test_images_workflow.py): the front-end step renamed "visual tests" and its report upload.
- [`tests/conventions/mono_repo/frontend/test_frontend_e2e.py`](../../../tests/conventions/mono_repo/frontend/test_frontend_e2e.py): the convention checks, with the visual ones limited to front ends whose specs call `toHaveScreenshot` ([`tests/conventions/mono_repo/frontend/test_frontend_e2e.py:43-50`](../../../tests/conventions/mono_repo/frontend/test_frontend_e2e.py#L43-L50)).
- [`.claude/skills/write-specs/scripts/specs.py`](../../../.claude/skills/write-specs/scripts/specs.py), [`.claude/skills/write-specs/scripts/spec_check.py`](../../../.claude/skills/write-specs/scripts/spec_check.py), [`.claude/skills/write-specs/SKILL.md`](../../../.claude/skills/write-specs/SKILL.md): `palettise` and the check message that names it. [`tests/harness/write_specs/test_palettise.py`](../../../tests/harness/write_specs/test_palettise.py) and [`tests/harness/write_specs/helpers.py`](../../../tests/harness/write_specs/helpers.py) test it.
- [`docs/specs/functional/use-cases/UC-029-create-an-operator.md`](../../../docs/specs/functional/use-cases/UC-029-create-an-operator.md): rows A1, KO, A2, OK set to 📸 Screenshot. The eight PNGs of `docs/specs/screens/UC-029/` ([`a1.png`](../../../docs/specs/screens/UC-029/a1.png), [`a1.dark.png`](../../../docs/specs/screens/UC-029/a1.dark.png), [`ko.png`](../../../docs/specs/screens/UC-029/ko.png), [`ko.dark.png`](../../../docs/specs/screens/UC-029/ko.dark.png), [`a2.png`](../../../docs/specs/screens/UC-029/a2.png), [`a2.dark.png`](../../../docs/specs/screens/UC-029/a2.dark.png), [`ok.png`](../../../docs/specs/screens/UC-029/ok.png), [`ok.dark.png`](../../../docs/specs/screens/UC-029/ok.dark.png)) are the captures. The four mock-ups of `docs/specs/screens/mockups/UC-029/` are deleted.
- [`AGENT.md`](../../../AGENT.md), [`qa/README.md`](../../../qa/README.md), [`.claude/rules/enforcement.json`](../../../.claude/rules/enforcement.json): the commands, the explanation of the visual tests, and the new enforcers of SPEC-12 and SPEC-13.

## 🧪 How to test it

```bash
pnpm --filter ./qa/e2e test
pnpm --filter @swarm/back-office typecheck
uv run pytest tests/conventions/mono_repo/frontend/test_frontend_e2e.py tests/ci/e2e tests/infra/images/test_back_office_image.py tests/harness/write_specs/test_palettise.py -n 2
python3 .claude/skills/write-specs/scripts/specs.py check
docker build -f frontend/apps/back-office/Dockerfile -t ghcr.io/gpbcom/swarm/back-office:local .
SWARM_IMAGE_TAG=local pnpm --filter @swarm/back-office run e2e
```

## 🔗 Evidence

- [Unit tests of the visual set-up](tests-evidences/test.txt): the qa/e2e tests pass.
- [pytest](tests-evidences/pytest.txt): the Python tests of the ticket pass.
- [specs check](tests-evidences/specs-check.txt): empty, so `specs.py check` prints nothing.
- [Lint](tests-evidences/lint.txt), [type check](tests-evidences/typecheck.txt), [mypy](tests-evidences/mypy.txt), [ruff check](tests-evidences/ruff-check.txt), [ruff format](tests-evidences/ruff-format.txt): clean.
- [Ticket references](tests-evidences/ticket-refs.txt), [plan view](tests-evidences/plan-view.txt), [pnpm install](tests-evidences/pnpm-install.txt), [swarm_core install](tests-evidences/swarm-core-install.txt) and [swarm_core wheel](tests-evidences/swarm-core-wheel.txt): set-up outputs.

## 📝 Assumptions accepted

- A large difference is more than 2 % of pixels beyond a per-pixel threshold of 0.2: TICKET.md leaves the figure to the plan, it is recorded and tested, and it absorbs palettisation noise.
- Sample data comes from Playwright route stubs of the gateway and the identity provider, with the visual identity's cast: the image is real, and no backend or real Operator data is involved.
- T0.20 adds the Back office image (nginx-unprivileged, port 8080) because T0.16 delivered none: AGENT.md requires one image per front end.
- The Back office e2e service is on `127.0.0.1:8181` because Ground control holds 8180: the person approved it, and a test keeps host ports distinct.
- The visual checks of the convention test apply only to front ends whose e2e calls `toHaveScreenshot`: the person decided it. Ground control keeps the shared set-up and no `webServer`.
- Screens are captured with locale en-GB, time zone UTC and scale 1 at 1280 x 800, as the visual identity's screenshot rules say.
- The `@difference` test proves AC1 by comparing A1 with the KO PNG under `test.fail()`, and a capture skips it, guarded twice (`--grep-invert` and the update skip).
- BR-008 is linked although the roadmap names no rule, and the ticket link points to the S04 anchor with no budget touched: both come from UC-029 and the roadmap.

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| [`.github/workflows/images.yml`](../../../.github/workflows/images.yml), [`tests/ci/images/test_images_workflow.py`](../../../tests/ci/images/test_images_workflow.py) | Drop the duplicate upload-artifact step, or remove the front-end path from the first step, and update `test_e2e_uploads_the_front_end_reports_on_failure` to match. |
| The eight PNGs of `docs/specs/screens/UC-029/` (for example [`a1.png`](../../../docs/specs/screens/UC-029/a1.png)) and [`tests-evidences/`](tests-evidences/test.txt) | Keep the output of one `SWARM_IMAGE_TAG=local pnpm --filter @swarm/back-office run e2e` run in `tests-evidences/`. If the first CI run fails on rasterisation, recapture in CI's image (the plan's own fallback). |
| [`qa/README.md`](../../../qa/README.md), [`AGENT.md`](../../../AGENT.md) | Update the sentences that still say the front-end tests "will live in" `e2e/` and that the front-end Docker rules are untested. |
| [`tests/conventions/mono_repo/frontend/test_frontend_e2e.py`](../../../tests/conventions/mono_repo/frontend/test_frontend_e2e.py) | Use a plain comprehension, or a small classmethod that returns the specs that call `toHaveScreenshot`. |
| [`frontend/apps/back-office/Dockerfile`](../../../frontend/apps/back-office/Dockerfile), [`tests/infra/images/test_back_office_image.py`](../../../tests/infra/images/test_back_office_image.py) | Copy only the manifests, install, then copy the sources so the install layer is cached. Otherwise drop the redundant `COPY`, and keep the test's manifest assertion in line. |
| [`tests/harness/write_specs/test_palettise.py`](../../../tests/harness/write_specs/test_palettise.py), [`tests/harness/write_specs/helpers.py`](../../../tests/harness/write_specs/helpers.py) | Move the constants and the two helper functions into `helpers.py`, or make them ClassVars and methods of `TestPalettise`. |
