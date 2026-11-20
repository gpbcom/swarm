# T0.04: CI checks for every language

**Status:** ✅ Done · **Branch:** `ticket/T0.04` · **Merged:** into `develop` locally, not pushed

## 🎯 What changed for users

- Every push and pull request now runs the CI pipeline. Only the checks that concern the changed code run, so a change to one service does not run the checks of the others.
- A change under `services/<name>/` runs that service only. A change under `packages/`, a lock file, a root workspace file or the pipeline itself runs everything that applies.
- Python services run ruff, `ruff format --check`, mypy and pytest, plus their slice of the convention tests. Rust runs cargo fmt, clippy with warnings as errors, and tests, when the Cargo workspace has members. TypeScript runs each project's lint, typecheck and test scripts, when a project has them. The specifications run `specs.py check`, which fails on any output.

## 🧩 What changed in the code

- `.github/workflows/ci.yml`: the entry point. Its first job runs the change detector on `git diff base..head` and prints the selection as outputs: the services, the TypeScript projects, and the rust, repository and specs flags. With no usable base commit (a new branch or a force push), it selects everything.
- `.github/scripts/detect_changes.py`: the change detector. Its shared-path lists (`SHARED_*`, `REPOSITORY_PREFIXES`, `SPECS_PREFIXES`) decide which paths run everything.
- `.github/workflows/python.yml`, `rust.yml`, `typescript.yml`, `specs.yml`: the four reusable workflows of step 2. Each waits for detection. The Python job runs a per-service matrix, and a repository job for `tests/` and `.github/scripts`.
- Every workflow uses a read-only token. Event values reach the shell only through `env`, never inlined into `run`.
- `tests/ci/`: the tests of the detector and of the workflows, in `detect_changes/` and `workflows/`.
- `AGENT.md`: now describes the real CI and the wider set of shared paths.
- `pyproject.toml` and `uv.lock`: PyYAML is added to the dev group so the tests can read the workflows.

## 🧪 How to test it

From the repository root:

```bash
uv sync
uv run ruff check tests/ci
uv run ruff format --check tests/ci
uv run pytest tests/ci/detect_changes -n 2
uv run pytest tests/ci/workflows -n 2
uv run python .claude/skills/write-specs/scripts/specs.py check
```

Run the test folders one at a time if needed, as AGENT.md asks.

## 🔗 Evidence

- [pytest output](tests-evidences/pytest.txt): 511 passed.
- [ruff check](tests-evidences/ruff-check.txt) and [ruff format](tests-evidences/ruff-format.txt).
- [mypy](tests-evidences/mypy.txt).
- [specs check](tests-evidences/specs-check.txt).
- [ticket references](tests-evidences/ticket-refs.txt) and [plan view](tests-evidences/plan-view.txt).
- [Review note](REVIEW.md): verdict ✅ Approved, 0 blocking findings.

## ✅ Acceptance criteria

| Criterion | Result |
| --- | --- |
| Given a pull request touching one service, when the CI runs, then only that service's checks run | ✅ Pass, see [REVIEW.md](REVIEW.md) |
| Given a pull request changing `packages/`, when the CI runs, then the checks of all the services and front ends that depend on it run | ✅ Pass, see [REVIEW.md](REVIEW.md) |

## 📌 Assumptions accepted by the reviewer

- Every lock file (`uv.lock`, `packages/rust/Cargo.lock`, `pnpm-lock.yaml`) runs everything. This is the conservative reading of the CI section of the deployment page and of AGENT.md.
- Benchmarks and the generated-types check are left to T0.07 and T0.06. The roadmap row of T0.04 does not list them, though the deployment page does.
- Rust and TypeScript are skipped while their workspaces are empty, as TKT-6 allows for a check whose target does not exist yet. An unparsable `Cargo.toml` should run cargo rather than skip it (follow-up).
- The test-structure choices: helper functions and constants in `helpers.py`, ClassVars, positional step order in the workflow tests, the literal `fromJSON` matrix, and `endswith` on the run steps. They are consistent with the tests rules of AGENT.md.
- AGENT.md wording and lock file names match the deployment page and the files on the branch.
- PyYAML in the dev group, and printing `GITHUB_OUTPUT`: accepted. The output holds no secret.
- Actions pinned by major tag, rustup reading `rust-toolchain.toml`, `rust-cache`, workflow names, and Python 3.12 through `setup-uv`: accepted. Pinning by SHA is a follow-up.
- ruff on `.github/scripts` and actionlint were not run: accepted. Adding their evidence is a follow-up.

## 🔜 Follow-ups

The non-blocking findings are listed in [PROGRESS.md](PROGRESS.md#-follow-ups).
