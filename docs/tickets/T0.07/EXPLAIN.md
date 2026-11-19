# T0.07: Rust core and benchmark gate

**Status:** ✅ Done · **Ticket:** [TICKET.md](TICKET.md) · **Choices and trade-offs:** [IMPLEMENTATION.md](IMPLEMENTATION.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🔭 What it does

- The Rust workspace holds three empty-shell crates, `safety`, `planner` and `mavlink`, each with one function and one criterion benchmark.
- A Python service can import those three functions from a wheel built by maturin, and each call releases the GIL.
- On every pull request, a CI job benchmarks the base commit and the pull request, and fails the build when a benchmark's mean is more than 5 % slower.

## ⚙️ How it works

1. **Workspace:** the three crates and the bindings are members, and `criterion` and `pyo3` are declared once for all of them, in [`packages/rust/Cargo.toml:3-17`](../../../packages/rust/Cargo.toml#L3-L17).
2. **A crate:** the safety shell sums its values with `wrapping_add`, so it never allocates or panics, in [`packages/rust/swarm-core/safety/src/lib.rs:10`](../../../packages/rust/swarm-core/safety/src/lib.rs#L10). `planner` and `mavlink` have the same shape ([`planner/src/lib.rs`](../../../packages/rust/swarm-core/planner/src/lib.rs), [`mavlink/src/lib.rs`](../../../packages/rust/swarm-core/mavlink/src/lib.rs)).
3. **A benchmark:** criterion times the function on 1,000 values, with the default harness switched off, in [`packages/rust/swarm-core/safety/benches/tick.rs:8-10`](../../../packages/rust/swarm-core/safety/benches/tick.rs#L8-L10) and [`packages/rust/swarm-core/safety/Cargo.toml:14-16`](../../../packages/rust/swarm-core/safety/Cargo.toml#L14-L16).
4. **The bindings:** each Python function takes a `Vec<u64>`, then calls the Rust crate inside `py.detach`, which releases the GIL, in [`packages/rust/swarm-core/python/src/lib.rs:12-15`](../../../packages/rust/swarm-core/python/src/lib.rs#L12-L15). The module registers the three functions at [`packages/rust/swarm-core/python/src/lib.rs:40-46`](../../../packages/rust/swarm-core/python/src/lib.rs#L40-L46). The type stub is [`swarm_core.pyi`](../../../packages/rust/swarm-core/python/swarm_core.pyi).
5. **The wheel:** the library is a `cdylib` that the workspace tests skip, so that `cargo test` never links libpython, in [`packages/rust/swarm-core/python/Cargo.toml:12-16`](../../../packages/rust/swarm-core/python/Cargo.toml#L12-L16). maturin alone enables `pyo3/extension-module`, in [`packages/rust/swarm-core/python/pyproject.toml:11-14`](../../../packages/rust/swarm-core/python/pyproject.toml#L11-L14).
6. **The CI check job:** `fmt`, `clippy` and `test` run first, in [`.github/workflows/rust.yml:10-29`](../../../.github/workflows/rust.yml#L10-L29).
7. **The base run:** the `bench` job runs only on pull requests, after `check`. It checks the base commit out into a worktree and saves the baseline `pr-base`, only if that commit has benchmarks, in [`.github/workflows/rust.yml:31-61`](../../../.github/workflows/rust.yml#L31-L61).
8. **The pull request run:** it compares against the baseline, with `--baseline-lenient` so that a missing baseline does not fail, in [`.github/workflows/rust.yml:62-63`](../../../.github/workflows/rust.yml#L62-L63).
9. **The gate:** the script reads every `change/estimates.json` under the criterion folder, in [`.github/scripts/bench_gate.py:98-111`](../../../.github/scripts/bench_gate.py#L98-L111). It takes `mean.point_estimate` ([`bench_gate.py:75-95`](../../../.github/scripts/bench_gate.py#L75-L95)) and fails when it is strictly above 0.05, in [`.github/scripts/bench_gate.py:136-148`](../../../.github/scripts/bench_gate.py#L136-L148). It runs from [`.github/workflows/rust.yml:64-65`](../../../.github/workflows/rust.yml#L64-L65). Exit 2 is a usage or data error, caught at [`bench_gate.py:130-132`](../../../.github/scripts/bench_gate.py#L130-L132).

## 🧱 Files and lines changed

<!-- changes -->
| File | Change | Lines in the new version | Added | Removed |
| --- | --- | --- | --- | --- |
| [`.github/scripts/bench_gate.py`](../../../.github/scripts/bench_gate.py) | Added | [1-152](../../../.github/scripts/bench_gate.py#L1) | +152 | −0 |
| [`.github/workflows/rust.yml`](../../../.github/workflows/rust.yml) | Modified | [30-65](../../../.github/workflows/rust.yml#L30) | +36 | −0 |
| [`AGENT.md`](../../../AGENT.md) | Modified | [25](../../../AGENT.md#L25), [30-36](../../../AGENT.md#L30), [62-64](../../../AGENT.md#L62), [114-119](../../../AGENT.md#L114), [168-169](../../../AGENT.md#L168) | +19 | −1 |
| [`packages/rust/Cargo.lock`](../../../packages/rust/Cargo.lock) | Modified | [5-22](../../../packages/rust/Cargo.lock#L5), [32-43](../../../packages/rust/Cargo.lock#L32), [62-67](../../../packages/rust/Cargo.lock#L62), [98-149](../../../packages/rust/Cargo.lock#L98), [169-234](../../../packages/rust/Cargo.lock#L169), [241-246](../../../packages/rust/Cargo.lock#L241), [304-314](../../../packages/rust/Cargo.lock#L304), [345-353](../../../packages/rust/Cargo.lock#L345), [410-425](../../../packages/rust/Cargo.lock#L410), [432-465](../../../packages/rust/Cargo.lock#L432), [485-541](../../../packages/rust/Cargo.lock#L485), [557-605](../../../packages/rust/Cargo.lock#L557), [634-642](../../../packages/rust/Cargo.lock#L634), [778-808](../../../packages/rust/Cargo.lock#L778), [854-859](../../../packages/rust/Cargo.lock#L854), [893-902](../../../packages/rust/Cargo.lock#L893), [997-1006](../../../packages/rust/Cargo.lock#L997), [1051-1091](../../../packages/rust/Cargo.lock#L1051), [1160-1179](../../../packages/rust/Cargo.lock#L1160) | +463 | −0 |
| [`packages/rust/Cargo.toml`](../../../packages/rust/Cargo.toml) | Modified | [3-10](../../../packages/rust/Cargo.toml#L3), [15-18](../../../packages/rust/Cargo.toml#L15) | +12 | −1 |
| [`packages/rust/swarm-core/mavlink/Cargo.toml`](../../../packages/rust/swarm-core/mavlink/Cargo.toml) | Added | [1-16](../../../packages/rust/swarm-core/mavlink/Cargo.toml#L1) | +16 | −0 |
| [`packages/rust/swarm-core/mavlink/benches/encode.rs`](../../../packages/rust/swarm-core/mavlink/benches/encode.rs) | Added | [1-14](../../../packages/rust/swarm-core/mavlink/benches/encode.rs#L1) | +14 | −0 |
| [`packages/rust/swarm-core/mavlink/src/lib.rs`](../../../packages/rust/swarm-core/mavlink/src/lib.rs) | Added | [1-12](../../../packages/rust/swarm-core/mavlink/src/lib.rs#L1) | +12 | −0 |
| [`packages/rust/swarm-core/mavlink/tests/encode.rs`](../../../packages/rust/swarm-core/mavlink/tests/encode.rs) | Added | [1-27](../../../packages/rust/swarm-core/mavlink/tests/encode.rs#L1) | +27 | −0 |
| [`packages/rust/swarm-core/planner/Cargo.toml`](../../../packages/rust/swarm-core/planner/Cargo.toml) | Added | [1-16](../../../packages/rust/swarm-core/planner/Cargo.toml#L1) | +16 | −0 |
| [`packages/rust/swarm-core/planner/benches/plan.rs`](../../../packages/rust/swarm-core/planner/benches/plan.rs) | Added | [1-14](../../../packages/rust/swarm-core/planner/benches/plan.rs#L1) | +14 | −0 |
| [`packages/rust/swarm-core/planner/src/lib.rs`](../../../packages/rust/swarm-core/planner/src/lib.rs) | Added | [1-12](../../../packages/rust/swarm-core/planner/src/lib.rs#L1) | +12 | −0 |
| [`packages/rust/swarm-core/planner/tests/plan.rs`](../../../packages/rust/swarm-core/planner/tests/plan.rs) | Added | [1-27](../../../packages/rust/swarm-core/planner/tests/plan.rs#L1) | +27 | −0 |
| [`packages/rust/swarm-core/python/Cargo.toml`](../../../packages/rust/swarm-core/python/Cargo.toml) | Added | [1-22](../../../packages/rust/swarm-core/python/Cargo.toml#L1) | +22 | −0 |
| [`packages/rust/swarm-core/python/pyproject.toml`](../../../packages/rust/swarm-core/python/pyproject.toml) | Added | [1-14](../../../packages/rust/swarm-core/python/pyproject.toml#L1) | +14 | −0 |
| [`packages/rust/swarm-core/python/src/lib.rs`](../../../packages/rust/swarm-core/python/src/lib.rs) | Added | [1-46](../../../packages/rust/swarm-core/python/src/lib.rs#L1) | +46 | −0 |
| [`packages/rust/swarm-core/python/swarm_core.pyi`](../../../packages/rust/swarm-core/python/swarm_core.pyi) | Added | [1-12](../../../packages/rust/swarm-core/python/swarm_core.pyi#L1) | +12 | −0 |
| [`packages/rust/swarm-core/safety/Cargo.toml`](../../../packages/rust/swarm-core/safety/Cargo.toml) | Added | [1-16](../../../packages/rust/swarm-core/safety/Cargo.toml#L1) | +16 | −0 |
| [`packages/rust/swarm-core/safety/benches/tick.rs`](../../../packages/rust/swarm-core/safety/benches/tick.rs) | Added | [1-14](../../../packages/rust/swarm-core/safety/benches/tick.rs#L1) | +14 | −0 |
| [`packages/rust/swarm-core/safety/src/lib.rs`](../../../packages/rust/swarm-core/safety/src/lib.rs) | Added | [1-12](../../../packages/rust/swarm-core/safety/src/lib.rs#L1) | +12 | −0 |
| [`packages/rust/swarm-core/safety/tests/tick.rs`](../../../packages/rust/swarm-core/safety/tests/tick.rs) | Added | [1-27](../../../packages/rust/swarm-core/safety/tests/tick.rs#L1) | +27 | −0 |
| [`tests/ci/bench_gate/helpers.py`](../../../tests/ci/bench_gate/helpers.py) | Added | [1-43](../../../tests/ci/bench_gate/helpers.py#L1) | +43 | −0 |
| [`tests/ci/bench_gate/test_bench_gate.py`](../../../tests/ci/bench_gate/test_bench_gate.py) | Added | [1-108](../../../tests/ci/bench_gate/test_bench_gate.py#L1) | +108 | −0 |
| [`tests/ci/workflows/test_rust_workflow.py`](../../../tests/ci/workflows/test_rust_workflow.py) | Modified | [38-63](../../../tests/ci/workflows/test_rust_workflow.py#L38), [73](../../../tests/ci/workflows/test_rust_workflow.py#L73), [76](../../../tests/ci/workflows/test_rust_workflow.py#L76), [78](../../../tests/ci/workflows/test_rust_workflow.py#L78), [120-173](../../../tests/ci/workflows/test_rust_workflow.py#L120) | +83 | −3 |
| [`tests/rust/swarm_core/helpers.py`](../../../tests/rust/swarm_core/helpers.py) | Added | [1-71](../../../tests/rust/swarm_core/helpers.py#L1) | +71 | −0 |
| [`tests/rust/swarm_core/test_swarm_core_layout.py`](../../../tests/rust/swarm_core/test_swarm_core_layout.py) | Added | [1-132](../../../tests/rust/swarm_core/test_swarm_core_layout.py#L1) | +132 | −0 |
| [`tests/rust/swarm_core/test_swarm_core_wheel.py`](../../../tests/rust/swarm_core/test_swarm_core_wheel.py) | Added | [1-61](../../../tests/rust/swarm_core/test_swarm_core_wheel.py#L1) | +61 | −0 |
| **27 files** | | | **+1481** | **−5** |
<!-- /changes -->

- [`packages/rust/Cargo.toml`](../../../packages/rust/Cargo.toml), lines [`3-17`](../../../packages/rust/Cargo.toml#L3-L17), and [`Cargo.lock`](../../../packages/rust/Cargo.lock): four new members and the two shared dependencies.
- [`packages/rust/swarm-core/safety`](../../../packages/rust/swarm-core/safety/src/lib.rs), [`planner`](../../../packages/rust/swarm-core/planner/src/lib.rs), [`mavlink`](../../../packages/rust/swarm-core/mavlink/src/lib.rs): the three shells, each with a `tests/` file and a `benches/` file.
- [`packages/rust/swarm-core/python`](../../../packages/rust/swarm-core/python/src/lib.rs): the bindings crate, its [`Cargo.toml`](../../../packages/rust/swarm-core/python/Cargo.toml), [`pyproject.toml`](../../../packages/rust/swarm-core/python/pyproject.toml) and stub.
- [`.github/workflows/rust.yml`](../../../.github/workflows/rust.yml), lines [`31-65`](../../../.github/workflows/rust.yml#L31-L65): the new `bench` job.
- [`.github/scripts/bench_gate.py`](../../../.github/scripts/bench_gate.py): the gate, in the style of `detect_changes.py`, with no class.
- [`AGENT.md`](../../../AGENT.md): the `cargo test`, `cargo bench` and maturin commands, the `bench` job, and a paragraph on the Rust core.
- [`tests/rust/swarm_core/test_swarm_core_layout.py`](../../../tests/rust/swarm_core/test_swarm_core_layout.py): checks the manifests, the stub and the uv exclusion. Every bindings test has "bindings" in its name.
- [`tests/rust/swarm_core/test_swarm_core_wheel.py`](../../../tests/rust/swarm_core/test_swarm_core_wheel.py) and [`helpers.py`](../../../tests/rust/swarm_core/helpers.py): build the wheel, install it in a fresh venv and call it. Each xdist worker gets its own target folder, at [`helpers.py:18-31`](../../../tests/rust/swarm_core/helpers.py#L18-L31).
- [`tests/ci/bench_gate/test_bench_gate.py`](../../../tests/ci/bench_gate/test_bench_gate.py) and [`helpers.py`](../../../tests/ci/bench_gate/helpers.py): run the script as a real process on real files.
- [`tests/ci/workflows/test_rust_workflow.py`](../../../tests/ci/workflows/test_rust_workflow.py), lines [`32-63`](../../../tests/ci/workflows/test_rust_workflow.py#L32-L63) and [`122-170`](../../../tests/ci/workflows/test_rust_workflow.py#L122-L170): helpers and one test per requirement of the `bench` job.

## 🧪 How to test it

```bash
cd packages/rust && cargo fmt --all --check && cargo clippy --workspace --all-targets --locked -- -D warnings && cargo test --workspace --locked
uv run pytest tests/rust/swarm_core -n 2
uv run pytest tests/ci/bench_gate tests/ci/workflows/test_rust_workflow.py -n 2
cd packages/rust && cargo bench --workspace --bench '*'
```

## 🔗 Evidence

- [cargo fmt](tests-evidences/cargo-fmt.txt), [clippy](tests-evidences/cargo-clippy.txt), [cargo test](tests-evidences/cargo-test.txt), [cargo metadata](tests-evidences/cargo-metadata.txt): the Rust checks.
- [ruff check](tests-evidences/ruff-check.txt), [ruff format](tests-evidences/ruff-format.txt), [mypy](tests-evidences/mypy.txt), [pytest](tests-evidences/pytest.txt), [specs check](tests-evidences/specs-check.txt): the Python and specification checks.
- [pytest -n 2, run 1](tests-evidences/pytest-n2-run1.txt), [run 2](tests-evidences/pytest-n2-run2.txt), [run 3](tests-evidences/pytest-n2-run3.txt): 39 passed each time, with the wheel built per worker.
- [Slowdown of the gate](tests-evidences/bench-gate-slowdown.txt): code slowed by +545 % fails the gate. It also records one failure of +12.15 % on identical code, from noise.
- [Plan view](tests-evidences/plan-view.txt) and [ticket references](tests-evidences/ticket-refs.txt): the plan and the links.

## 📝 Assumptions accepted

None.

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| [`packages/rust/swarm-core/python/pyproject.toml`](../../../packages/rust/swarm-core/python/pyproject.toml) | `skip-auditwheel = true` was added only to reduce the xdist race. Now that each worker has its own target folder, remove it so the wheel is checked for manylinux again, or say in Notes why it stays. |
| [`.github/scripts/bench_gate.py`](../../../.github/scripts/bench_gate.py) | The gate compares only `mean.point_estimate`. The evidence shows +12.15 % on identical code, so shared runners will sometimes fail for no reason. Consider the lower bound of `mean.confidence_interval`, or a rerun. Keep the "more than 5 % fails" contract and its tests. |
| [`tests/rust/swarm_core/test_swarm_core_wheel.py`](../../../tests/rust/swarm_core/test_swarm_core_wheel.py) | Lines [15-20](../../../tests/rust/swarm_core/test_swarm_core_wheel.py#L15-L20): the class-scoped fixture is an instance method, so pytest warns `PytestRemovedIn10Warning`. Move it to a `conftest.py` or make it a `@classmethod`. |
| [`tests-evidences/ruff-check.txt`](tests-evidences/ruff-check.txt) | The ruff check and format evidence list only the test files. CI also lints `.github/scripts`, so add [`bench_gate.py`](../../../.github/scripts/bench_gate.py) to both commands. |
| [`tests/ci/workflows/test_rust_workflow.py`](../../../tests/ci/workflows/test_rust_workflow.py) | Lines [157-160](../../../tests/ci/workflows/test_rust_workflow.py#L157-L160): the comparison step is found by the flag order `cargo bench --workspace --locked`, which forced the base step to swap its flags. Look for `--baseline-lenient pr-base` instead. |
| [`tests-evidences/pytest-n2-run1.txt`](tests-evidences/pytest-n2-run1.txt) | The three `-n 2` logs ([run 2](tests-evidences/pytest-n2-run2.txt), [run 3](tests-evidences/pytest-n2-run3.txt)) open with a uv `VIRTUAL_ENV` warning and omit the command (`uv run pytest tests/rust/swarm_core -n 2`). Put it at the top of each. |
