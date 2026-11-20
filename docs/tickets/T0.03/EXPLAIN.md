# T0.03: Convention tests and linters: explanation

**Status:** ✅ Done · **Ticket:** [TICKET.md](TICKET.md) · **Plan:** [PLAN.md](PLAN.md) · **Progress:** [PROGRESS.md](PROGRESS.md)

## What changed for users

Developers now get the AGENT.md rules checked by the test suite, and the Rust and TypeScript workspaces have strict lint and type settings.

- **Convention tests:** seven rules from AGENT.md fail the test run when a service breaks them: one class per file, five files per folder, no `Any`, no nested function, allowed layer imports, lifecycle base classes, and Pydantic models only in `models/`.
- **New services are covered automatically:** every direct sub-folder of `services/` is checked, so a new service needs no change to the tests.
- **Rust settings:** `packages/rust` has a rustfmt configuration and workspace-wide clippy and rustc lints that crates opt in to.
- **TypeScript settings:** `packages/ts` has a new shared package, `@swarm/config`, with a strict `tsconfig.base.json` and an eslint flat configuration.

## What changed in the code

- `tests/conventions/rules/`: one `ConventionRule` subclass per rule, reading the source as a syntax tree. The `ConventionRules` registry lists all seven. The layer rule, the code rules and the file rules each sit in their own folder.
- `tests/conventions/rules/service_tree.py`: finds the services under `services/` and their layers and packages.
- `tests/conventions/services/test_service_conventions.py`: runs every rule against every service. The `SWARM_CONVENTIONS_SERVICES_ROOT` variable points the run at another folder.
- `tests/conventions/linters/`: tests that the Rust and TypeScript settings are in place and strict.
- `tests/conventions/samples/`: a deliberately broken sample service and an empty sample service, both written into `tmp_path` from strings, so no broken code sits in the repository.
- `packages/rust/Cargo.toml` and `packages/rust/rustfmt.toml`: the workspace lints (clippy `all` as an error, `pedantic` as a warning, `missing_docs` as a warning) and the rustfmt options (120-character lines, stable options only).
- `packages/ts/config/`: the `@swarm/config` package (`package.json`, `tsconfig.base.json`, `tsconfig.json` and `eslint.config.js`). Its typescript-eslint configuration uses `strictTypeChecked` and `stylisticTypeChecked`. Versions are pinned, and `pnpm-lock.yaml` records them.
- `pyproject.toml`: `known-first-party = ["tests"]` in the ruff isort section, so test files written before their modules keep a stable import order.
- `AGENT.md`: a paragraph on the rules now enforced, and the Rust and TypeScript commands.

## How to test it

From the repository root:

```bash
uv run ruff check tests packages services
uv run pytest tests/conventions/rules -n 2
uv run pytest tests/conventions/samples -n 2
uv run pytest tests/conventions/services -n 2
uv run pytest tests/conventions/linters -n 2
```

AGENT.md asks for one file or one folder at a time, so run each folder on its own when you debug a failure. The sample services do the work of the end-to-end check, in `tests/conventions/samples/`: the broken sample service must fail once per rule, and the empty sample service must pass with no change to the tests.

The first expects `7 failed`, one per rule. The second expects every rule to pass for an empty service beside a copy of gateway.

For the TypeScript and Rust settings, from their workspace folders:

```bash
pnpm -r --if-present lint
pnpm -r --if-present typecheck
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
```

`cargo fmt` and `cargo clippy` do not apply yet, because `packages/rust` has no crate.

## Evidence

All in [tests-evidences/](tests-evidences/):

- [pytest.txt](tests-evidences/pytest.txt): 387 passed, including the broken-service and empty-service checks.
- [ruff-check.txt](tests-evidences/ruff-check.txt) and [ruff-format.txt](tests-evidences/ruff-format.txt): ruff passes on every changed file.
- [mypy.txt](tests-evidences/mypy.txt): mypy passes.
- [lint.txt](tests-evidences/lint.txt): eslint passes.
- [typecheck.txt](tests-evidences/typecheck.txt): tsc passes.
- [specs-check.txt](tests-evidences/specs-check.txt): the specification check passes.
- [cargo-metadata.txt](tests-evidences/cargo-metadata.txt): the Cargo workspace metadata.
- [pnpm-install.txt](tests-evidences/pnpm-install.txt): the pnpm install.
- [test.txt](tests-evidences/test.txt), [plan-view.txt](tests-evidences/plan-view.txt) and [ticket-refs.txt](tests-evidences/ticket-refs.txt): further outputs of the run.

The review note is in [REVIEW.md](REVIEW.md).

## Assumptions accepted by the reviewer

- **K21, imports sorted alphabetically by module path:** accepted. ruff passes on every changed file ([ruff-check.txt](tests-evidences/ruff-check.txt)), and no specification sets an order.
- **Seven rules only:** accepted. The roadmap row names these seven, so `@staticmethod`, underscore attributes and the node rules are left for later. AGENT.md says which rules are not tested yet.
- **Strictest options for rustfmt, clippy, eslint and tsc:** accepted as the conservative choice (TKT-8). The roadmap says "strict" for `tsc`.
- **`tests/conventions/mono_repo/` unchanged:** accepted. The diff does not touch it.
- **Discovery covers `services/` only:** accepted. The ticket names `services/`, and `packages/python/` is empty.
- **Layer imports checked in `src/<package>/<layer>/` only:** accepted. A bare top-level layer name such as `from service.x import Y` counts as that layer, as AGENT.md defines layers.
- **Lifecycle and Pydantic base classes recognised by name:** accepted. The real lifecycle classes arrive in T0.05.
- **Broken and empty sample services written into `tmp_path`:** accepted. The enforcement test runs in a child process, which keeps ruff, mypy and the real `services/` folder free of deliberately broken code.
- **`known-first-party = ["tests"]` for ruff:** accepted. The fix is minimal and recorded in PROGRESS.md, and no other file changes its import order.

## 🔜 Follow-ups

Non-blocking findings. They do not hold the merge (TKT-12).

| File | What to change |
| --- | --- |
| `AGENT.md` | K10, lines 112-121: the new 'Since T0.03, ...' paragraph sits between 'tests/conventions/ fails on any of these, in src/ and tests/ unless stated:' and the bullet list that colon introduces. Move it after the list, and mark in the list which bullets are enforced. In the same way, the new Rust and TypeScript block (lines 17-28) separates the uv commands from the bullets about them. Move it below those bullets. |
| `tests/conventions/rules/code/no_any.py` | K16, lines 41-48: the rule misses 'import typing as t' followed by 't.Any', and 'from typing import *'. Resolve module aliases from the Import nodes, and report a star import from typing or typing_extensions. |
| `tests/conventions/linters/test_typescript_settings.py` | K09, line 14: declare PACKAGE as ClassVar[str], as test_rust_settings.py and test_layer_imports.py already do. |
| `tests/conventions/helpers.py` | K01: AGENT.md says that tests/conventions/helpers.py holds the third-party protocol names that are exempt from the underscore-attribute rule. The new helpers.py holds no such list, because that rule is out of scope. When the rule is added, put the list here, or update the AGENT.md sentence. |
| `tests/conventions/samples/test_empty_service.py` | K06, lines 99-103: the assertion '14 passed' depends on the real gateway passing all seven rules and on the number of rules. Derive the count from len(ConventionRules.all()) times the number of services, so that adding a rule does not break this test. |
| `packages/rust/Cargo.toml` | K12: no crate exists yet, so cargo fmt and clippy have not been run against these settings (tests-evidences only holds cargo-metadata.txt). Run them on the first real crate in T0.07, and check that the crate has '[lints] workspace = true'. |

## Timings

The elapsed times and tokens of the ticket are in the ⏱️ Timings section of [PROGRESS.md](PROGRESS.md), measured by the harness (TKT-10).
