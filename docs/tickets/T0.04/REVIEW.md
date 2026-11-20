# T0.04: Review note

**Verdict:** ✅ Approved · **Branch:** `ticket/T0.04`

## What changed

- Every push and pull request now runs `ci.yml`. Its first job runs a change detector on `git diff base..head` and prints five outputs: the services, the TypeScript projects, and the rust, repository and specs flags. With no usable base commit (a new branch or a force push), it selects everything.
- A changed path under `services/<name>/` selects only that service. A changed path under `packages/`, any lock file, a root workspace file (`pyproject.toml`, `package.json`, `pnpm-workspace.yaml`, `turbo.json`) or a file of the pipeline itself selects everything that applies.
- Step 2 runs as four reusable workflows that wait for detection:
  - **Python:** a per-service matrix of ruff, `ruff format --check`, mypy, pytest and that service's slice of the convention tests, plus a repository job for `tests/` and `.github/scripts`.
  - **Rust:** cargo fmt, clippy `-D warnings` and tests, `--locked`, only when the Cargo workspace has members.
  - **TypeScript:** each project's lint, typecheck and test scripts through pnpm `--if-present`.
  - **Specifications:** `specs.py check`, which fails on any output.
- Every workflow uses a read-only token, and event values reach the shell only through `env`, never inlined into `run`.
- AGENT.md now describes the real CI and the wider set of shared paths. PyYAML is added to the dev group so the tests can read the workflows.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given a pull request touching one service, when the CI runs, then only that service's checks run | `TestDetectChanges::test_a_pull_request_touching_one_service_selects_only_that_service`, `TestCiWorkflow` job-condition tests, `TestPythonWorkflow::test_the_services_job_runs_only_its_slice_of_the_convention_tests`; tests-evidences/pytest.txt (511 passed) | ✅ Pass |
| 2. Given a pull request changing `packages/`, when the CI runs, then the checks of all the services and front ends that depend on it run | `TestSharedChanges::test_a_shared_path_alone_runs_everything` (packages/python, packages/ts, packages/rust and the lock files), `test_all_runs_everything_with_empty_stdin`; tests-evidences/pytest.txt | ✅ Pass |

## Look at first

- **What counts as shared.** `SHARED_*`, `REPOSITORY_PREFIXES` and `SPECS_PREFIXES` decide which paths run everything. Read them once to confirm the list matches your intent; for example, `terraform.yml` and AGENT.md select nothing. File: `.github/scripts/detect_changes.py` (lines 26-43).
- **Base commit and fail-safe.** The detect step picks the PR base or `before`, and falls back to `--all` when that commit is missing. A failed `git diff` would select nothing, because the pipe has no pipefail (follow-up). File: `.github/workflows/ci.yml` (lines 27-47).
- **Per-service isolation of the checks.** The matrix entry reaches the shell only through `env`, and the convention tests are sliced with `-k "$SERVICE-"`. File: `.github/workflows/python.yml` (lines 20-61).
- **Specs gate.** The step fails on any output or on a non-zero exit. On a non-zero exit, the captured output is not printed (follow-up). File: `.github/workflows/specs.yml`.
- Operator isolation, Simulator isolation and identity: not touched by this ticket. It handles no secret, and every token is `contents: read`.

## Assumptions accepted

- TICKET: every lock file runs everything: accepted, the conservative reading of 09-deployment#ci and AGENT.md.
- TICKET: benchmarks and the generated-types check go to T0.07 and T0.06: accepted. The roadmap row does not list them, though 09-deployment#ci does.
- TICKET and K09: Rust and TypeScript are skipped while their workspaces are empty: accepted under TKT-6. An unparsable Cargo.toml should run cargo rather than skip it (follow-up).
- K01 to K07: the test-structure choices (helpers.py functions, ClassVars, positional step order, the literal fromJSON matrix, endswith on run steps): accepted, consistent with AGENT.md Tests.
- K08: AGENT.md wording and lock file names: accepted. They match 09-deployment#ci and the files on the branch.
- K10 and K11: PyYAML in the dev group, and printing GITHUB_OUTPUT: accepted. The output holds no secret.
- K12 to K15: actions pinned by major tag, rustup reading rust-toolchain.toml, rust-cache, workflow names, Python 3.12 through setup-uv: accepted. Pinning by SHA is a follow-up.
- K12 and K14: ruff on `.github/scripts` and actionlint were not run: accepted. Adding their evidence is a follow-up.

## Follow-ups

- specs.yml: print the output of `specs.py check` even when it exits non-zero (K15).
- ci.yml: add pipefail to the detect step so a failed `git diff` cannot select nothing (K11).
- detect_changes.py: when Cargo.toml exists but is unreadable, run the Rust checks rather than skip them (K09).
- python.yml: anchor the `-k "$SERVICE-"` slice so one service name cannot match another (K12).
- Pin third-party actions by commit SHA before T0.10 (K11 to K15).
- ci.yml: limit `push` to `develop` and `master` so PR branches do not run the pipeline twice (K11).
- Add ruff check and format evidence for `.github/scripts/detect_changes.py`, and an actionlint run, to `tests-evidences/` (verifier).
- test_detect_changes.py: move the module-level `NOTHING` into helpers.py or a ClassVar (K01).
