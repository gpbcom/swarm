# T0.20: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- A screen that differs by more than an allowed amount fails the build, in light and dark mode, and the figure is left to the plan ([TICKET.md](TICKET.md)).
- The Playwright tests run against the real images started by compose, never a dev server, and the shared set-up refuses a `webServer` ([`AGENT.md`](../../../AGENT.md)).
- A screenshot is 1280 x 800 at scale 1, with the sample cast, and a 256-colour palette PNG ([`docs/specs/visual-identity.md`](../../../docs/specs/visual-identity.md), SPEC-12).
- One image per front end, a multi-stage Dockerfile with the repository root as context ([`AGENT.md`](../../../AGENT.md)).
- Class, import and raw-string rules of AGENT.md, and no module-level code, apply to the Python tests.

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | What counts as a large difference | 2 % of pixels beyond a threshold of 0.2 | A stricter or zero tolerance | A small real change can pass unseen |
| [D2](#d2) | Where the sample data comes from | Playwright route stubs | The real gateway and identity provider in compose | The backend is not exercised |
| [D3](#d3) | Which front ends the visual checks apply to | Only those whose e2e calls `toHaveScreenshot` | All front ends, with a visual config for Ground control | Ground control has no visual guard yet |
| [D4](#d4) | Host port of the Back office service | `127.0.0.1:8181` | Another port, or a shared one | A port to remember, kept distinct by a test |
| [D5](#d5) | How a large difference is proved | A `@difference` test under `test.fail()` | A unit test of the tolerance alone | A test that must be skipped in a capture |
| [D6](#d6) | Where the Back office image comes from | This ticket builds it | Wait for T0.16 | Scope grows |
| [D7](#d7) | How RGB captures become palette PNGs | A `specs.py palettise` command | Palettise by hand, or in the renderer | One more command to learn |

## <a id="d1"></a>D1: What counts as a large difference

**Chosen:** `maxDiffPixelRatio` 0.02 and `threshold` 0.2 · **Where:** [`qa/e2e/src/define-visual-config.ts:72-80`](../../../qa/e2e/src/define-visual-config.ts#L72-L80) · **Source:** plan, accepted by the reviewer

| Option | For | Against |
| --- | --- | --- |
| ✅ 2 % and 0.2 | The ticket leaves the figure to the plan. Palettisation changes colours slightly, and this absorbs it. The figure is exported and pinned by [`qa/e2e/test/define-visual-config.test.ts:98`](../../../qa/e2e/test/define-visual-config.test.ts#L98). | A change touching under 2 % of the pixels passes. |
| A stricter tolerance | Catches small changes. | The baselines are palette PNGs while the app renders full colour, so noise could fail every run. No measurement was made to choose a lower figure. |

**Trade-off:** small visual drift is accepted in return for stable runs.

**Revisit when:** CI renders with other fonts and fails, or a real regression slips under 2 %.

## <a id="d2"></a>D2: Where the sample data comes from

**Chosen:** route stubs for the gateway and the identity provider · **Where:** [`frontend/apps/back-office/e2e/sample-data.ts:153-158`](../../../frontend/apps/back-office/e2e/sample-data.ts#L153-L158) · **Source:** read from the diff, accepted by the reviewer

| Option | For | Against |
| --- | --- | --- |
| ✅ Stubs | The cast of the visual identity is fixed and the time is fixed, so screens repeat. The compose stack needs only the front-end image. | The unsigned tokens and answers are test code that mimics identity, and Operator isolation is not exercised. |
| Real backend in compose | Closer to production. | No compose service for the gateway or identity exists in [`infra/compose/e2e.yaml`](../../../infra/compose/e2e.yaml), and the cast would have to be seeded. Not evaluated further by the workers: open point. |

**Trade-off:** screens are deterministic, the backend contract is not tested here.

**Revisit when:** a compose stack with the gateway exists.

## <a id="d3"></a>D3: Which front ends the visual checks apply to

**Chosen:** the checks apply only to front ends whose specs call `toHaveScreenshot` · **Where:** [`tests/conventions/mono_repo/frontend/test_frontend_e2e.py:43-50`](../../../tests/conventions/mono_repo/frontend/test_frontend_e2e.py#L43-L50) · **Source:** the person, 13:40

| Option | For | Against |
| --- | --- | --- |
| ✅ Only front ends that compare screens | Ground control keeps its shared set-up and no `webServer`, with no new config. | A front end that never compares screens has no visual guard. |
| Ground control gets a visual config and a `capture` script now | Every front end has the same set-up. | It adds work for screens Ground control does not yet compare, outside the ticket. |

**Trade-off:** coverage grows with each front end's own screens.

**Revisit when:** Ground control compares screens.

## <a id="d4"></a>D4: Host port of the Back office service

**Chosen:** `127.0.0.1:8181:8080` · **Where:** [`infra/compose/e2e.yaml:14-19`](../../../infra/compose/e2e.yaml#L14-L19) · **Source:** the person, 13:40

| Option | For | Against |
| --- | --- | --- |
| ✅ 8181 | Ground control holds 8180, so both suites run side by side in CI. [`tests/ci/e2e/test_compose_e2e.py:106`](../../../tests/ci/e2e/test_compose_e2e.py#L106) refuses duplicates. | Each front end needs its own port. |
| Reuse 8180 | No new port. | The two suites would clash. |

**Trade-off:** a new host port per front end.

**Revisit when:** more front ends join compose.

## <a id="d5"></a>D5: How a large difference is proved

**Chosen:** compare A1 with the KO PNG under `test.fail()`, skipped in a capture · **Where:** [`frontend/apps/back-office/e2e/create-an-operator.spec.ts:91-97`](../../../frontend/apps/back-office/e2e/create-an-operator.spec.ts#L91-L97) · **Source:** read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ `@difference` test | Proves AC1 on the real app and baselines, in both modes. | A capture would overwrite KO with A1, so it is guarded twice: [`frontend/apps/back-office/package.json:11`](../../../frontend/apps/back-office/package.json#L11) and the skip. |
| Unit tests of the tolerance only | No risk to the baselines. | Show the constants, not that a build fails. They exist too ([`qa/e2e/test/define-visual-config.test.ts`](../../../qa/e2e/test/define-visual-config.test.ts)). |

**Trade-off:** a double guard for a stronger proof.

**Revisit when:** Playwright offers a way to assert a mismatch without a baseline.

## <a id="d6"></a>D6: Where the Back office image comes from

**Chosen:** this ticket adds [`frontend/apps/back-office/Dockerfile`](../../../frontend/apps/back-office/Dockerfile) · **Source:** read from the diff, accepted by the reviewer

| Option | For | Against |
| --- | --- | --- |
| ✅ Build it here | AGENT.md requires one image per front end, and compose needs it to run the tests. | T0.16 delivered none, so scope grows. |
| Wait for another ticket | Keeps scope small. | The ticket could not meet its acceptance criteria. |

**Trade-off:** extra scope for a working pipeline. The Dockerfile has a redundant `COPY` (see follow-ups in [EXPLAIN.md](EXPLAIN.md)).

**Revisit when:** another ticket owns the image.

## <a id="d7"></a>D7: How RGB captures become palette PNGs

**Chosen:** `specs.py palettise` · **Where:** [`.claude/skills/write-specs/scripts/specs.py:129-141`](../../../.claude/skills/write-specs/scripts/specs.py#L129-L141) · **Source:** read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ A command | Idempotent, limited to a group, tested by [`tests/harness/write_specs/test_palettise.py`](../../../tests/harness/write_specs/test_palettise.py), and the check message names it. | One more command. |
| Palettise by hand | No code. | `specs.py check` refuses RGB PNGs, and by-hand work does not repeat. |

**Trade-off:** a small harness addition for a repeatable capture.

**Revisit when:** Playwright can write palette PNGs itself.

## 📝 Assumptions behind the choices

- 2 % and 0.2 accepted: supports [D1](#d1).
- Stubbed data with the visual identity's cast: supports [D2](#d2).
- Visual checks only for front ends that compare screens: supports [D3](#d3).
- Port 8181 approved by the person: supports [D4](#d4).
- `@difference` guarded twice: supports [D5](#d5).
- T0.20 adds the image because T0.16 delivered none: supports [D6](#d6).
