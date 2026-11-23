# T0.14: Review note

**Verdict:** ✅ Approved (round 2, confirming fixes) · **Branch:** `feature/tickets`

## What changed

- The Linux job of the desktop workflow no longer installs `libappindicator3-dev`, which `ubuntu-latest` (24.04 and later) no longer ships. It still installs `libwebkit2gtk-4.1-dev`, `librsvg2-dev` and `patchelf`. The shell has no tray icon, so it needs no appindicator library.
- The lock file's peer resolution changed (`supports-color`) after a fresh install. This round also wrote the tests evidence of every check, run on the ticket's own files in a clean tree.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given a token changed on the visual identity page, when one build runs, then the apps and the mock-ups show the change | tests/harness/write_specs/test_tokens_package.py (tests-evidences/pytest.txt, 2436 passed); tests-evidences/specs-check.txt (empty) | ✅ Pass |
| 2. Given the four shells, when each is opened in light mode and in dark mode, then each opens | tests-evidences/test.txt (packages/ts/ui 154 tests; back-office 8, mission-studio 8, ground-control 10, client-portal 9) | ✅ Pass |
| 3. Given the Tauri 2 desktop shell, when it is built on Windows, macOS and Linux, then it builds on each | tests/ci/workflows/test_desktop_workflow.py; .github/workflows/desktop.yml (matrix of the three OS, Linux libraries fixed) | ✅ Pass locally; the real build is confirmed by the `desktop` CI run on the pull request |

## Look at first

- The Linux libraries of Tauri: .github/workflows/desktop.yml, line 57. `automerge.yml` waits for `desktop`, so the shared pull request depends on this job.
- The shared lock file: pnpm-lock.yaml. It now also holds T0.12's `packages/ts/api-client` importer. See the follow-ups.
- Identity, Operator isolation and Simulator isolation: not touched by this fix round.

## Assumptions accepted

- No feature or use case is linked, and BR-017 is linked only through the epic. Accepted: languages belong to T0.15.
- The ticket link points to the sprint anchor `#s03`. Accepted: the roadmap row has no anchor of its own.
- `➖ No screen`. Accepted: the shells are empty frames, and the UC-029 screenshots belong to T0.20.

## Follow-ups

- pnpm-lock.yaml holds T0.12's `api-client` entries. T0.10 and T0.12 also own the file. Decide at `finish` which ticket commits the lock, or regenerate it on T0.14's own tree (K11).
- Add a test that the Linux step does not install `libappindicator3-dev`, so the package cannot come back (K11).
