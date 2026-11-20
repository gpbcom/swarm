# T0.03: Review note

**Verdict:** ✅ Approved · **Branch:** `ticket/T0.03`

## What changed

- Seven AGENT.md rules are now checked by tests: one class per file, five files per folder, no `Any`, no nested function, allowed layer imports, lifecycle base classes, and Pydantic models only in `models/`. Each rule is a `ConventionRule` subclass that reads the source as a syntax tree, and the `ConventionRules` registry lists all seven.
- `test_service_conventions.py` runs every rule against every folder it finds under `services/`. Nothing names a service, so a new one is covered automatically. The `SWARM_CONVENTIONS_SERVICES_ROOT` variable points the run at another folder.
- In `packages/rust`, rustfmt allows 120-character lines and uses stable options only. Clippy treats `all` as an error and `pedantic` as a warning, and `missing_docs` is a warning. Crates opt in to these lints.
- In `packages/ts`, a new shared package `@swarm/config` holds the strict `tsconfig.base.json` and an eslint flat config with typescript-eslint `strictTypeChecked` and `stylisticTypeChecked`. Versions are pinned and recorded in `pnpm-lock.yaml`.
- One decision outside the plan: `tests` is declared first-party for ruff's import sorting, so test files written before their modules keep a stable import order. It is recorded in PROGRESS.md.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. **Given** a deliberately broken sample service, **when** the convention tests run against it, **then** each rule of the ticket fails once | `TestBrokenService::test_the_convention_tests_fail_once_per_rule`: a real pytest child process reports exactly `7 failed` and one `FAILED [broken-<rule>]` per rule. Also `test_each_rule_reports_exactly_one_violation`. Run in `tests-evidences/pytest.txt` (387 passed) | ✅ Pass |
| 2. **Given** an empty service added under `services/`, **when** the convention tests run, **then** they need no change and pass for it | `TestEmptyService::test_the_convention_tests_pass_unchanged`, with a skeleton service and a bare one beside a copy of gateway, giving 14 passed. Also `test_no_convention_test_names_the_empty_service`. Run in `tests-evidences/pytest.txt` | ✅ Pass |

Other checks: `ruff-check.txt`, `ruff-format.txt`, `mypy.txt`, `lint.txt` (eslint), `typecheck.txt` (tsc) and `specs-check.txt` all pass. cargo fmt and clippy do not apply yet, because no crate exists.

## Look at first

- **Layer import resolution** (`tests/conventions/rules/layers/layer_imports.py`, `_absolute_names` and `_target_layer`). It resolves relative imports, treats a bare `from service.x` as the `service` layer, and skips `tests/` and files directly under `src/<package>/`. This is the rule most likely to give false positives or false negatives on real code.
- **How a service is found** (`tests/conventions/rules/service_tree.py`, `discover`, `layer_of` and `package_of`). Every direct sub-folder of `services/` counts as a service. This is what makes criterion 2 hold.
- **The end-to-end check** (`tests/conventions/samples/helpers.py` and `test_broken_service.py`). Look at how the broken sample breaks each rule exactly once. For example, `service/` holds exactly five modules, so only `crowded/` trips the folder limit.
- **The lifecycle and Pydantic rules** (`tests/conventions/rules/classes/`). They recognise base classes by name and follow inheritance within one service. Both apply to `tests/` as well, as AGENT.md says.
- The ticket touches no Operator isolation, Simulator isolation, identity, secret or hot-path budget.

## Assumptions accepted

- K21, imports sorted alphabetically by module path: accepted. ruff passes on every changed file.
- The seven rules from the roadmap row, with the other rules left for later: accepted. AGENT.md says which rules are not tested yet.
- Strictest options for rustfmt, clippy, eslint and tsc: accepted as the conservative choice (TKT-8).
- `tests/conventions/mono_repo/` left unchanged: accepted. The diff does not touch it.
- Only `services/` is walked, not `packages/python/`: accepted. The ticket names `services/` only.
- Layer imports checked in `src/<package>/<layer>/` only, with bare layer names counted as layers: accepted. This is how AGENT.md defines layers.
- Lifecycle and Pydantic base classes recognised by name: accepted. The real lifecycle classes arrive in T0.05.
- Sample services written into `tmp_path`, with the enforcement test run in a child process: accepted.
- `known-first-party = ["tests"]` for ruff: accepted. The fix is minimal, recorded in PROGRESS.md, and changes no other file's import order.

## Follow-ups

- AGENT.md (K10): move the "Since T0.03" paragraph after the rule list it interrupts, and move the Rust and TypeScript commands below the bullets about the uv commands.
- `no_any.py` (K16): also catch `import typing as t` with `t.Any`, and star imports from `typing`.
- `test_typescript_settings.py` (K09): declare `PACKAGE` as a `ClassVar`.
- `tests/conventions/helpers.py` (K01): AGENT.md says this file holds the exemption list for the underscore-attribute rule. Add the list when that rule arrives, or update the sentence.
- `test_empty_service.py` (K06): compute the expected `14 passed` from the rule and service counts instead of hard-coding it.
- `packages/rust` (K12): run cargo fmt and clippy on the first real crate (T0.07), and check it opts in with `[lints] workspace = true`.
