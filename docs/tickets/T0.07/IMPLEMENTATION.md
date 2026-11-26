# T0.07: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- A Python service imports a Rust function from a maturin wheel, and a slowdown of more than 5 % fails the pull request build ([TICKET.md](TICKET.md), acceptance criteria 1 and 2).
- CPU-heavy work releases the GIL ([engine page](../../specs/technical/04-engine.md#flight-engine)).
- No class twice in a file, no module-level code beyond the exceptions, no mocks, no nested function, at most five Python files per folder ([`AGENT.md`](../../../AGENT.md)).
- The CI repository job runs `uv run pytest tests -n 2`, so the wheel tests must pass under xdist (review round 3).
- `uv sync` must not build Rust, and `cargo clippy` and `cargo test` on the workspace must not need libpython ([`AGENT.md`](../../../AGENT.md)).

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | When maturin enables `extension-module` | In `[tool.maturin] features` | On the pyo3 dependency | A bare `cargo build` of the cdylib links libpython |
| [D2](#d2) | How the wheel tests avoid a build race under xdist | One Cargo target folder per worker | A file lock or one shared build | One full compile per worker on the first run |
| [D3](#d3) | Audit of the wheel | `skip-auditwheel = true` | Keep the audit on | No manylinux check, kept only as a mitigation |
| [D4](#d4) | Whether the bindings crate runs `cargo test` | `test = false`, `doctest = false` | `auto-initialize` feature | No Rust unit tests for the bindings |
| [D5](#d5) | How to pass data to Rust | `Vec<u64>` by value with `py.detach` | `&[u64]` with the GIL held, or a zero-copy buffer | One copy of the input |
| [D6](#d6) | Where the 5 % gate compares | `mean.point_estimate` against 0.05 | Confidence interval bound | Noise can fail a pull request |
| [D7](#d7) | The gate script's parsing and errors | Own parser, `ValueError`, exit 2 | `argparse` | A small manual option loop |
| [D8](#d8) | The base baseline | Worktree of the base SHA, saved as `pr-base` | Stored results | Benchmarks run twice per pull request |
| [D9](#d9) | Flag order of the base `cargo bench` | `--locked --workspace` | `--workspace --locked` | A test depends on flag order |
| [D10](#d10) | Shared dependency versions | `[workspace.dependencies]` | Per crate | One bump moves all crates |
| [D11](#d11) | Placeholder body | `fold` with `wrapping_add` | `iter().sum()` | Not explicitly vectorised |
| [D12](#d12) | Test layout for the wheel | One class-scoped fixture, `-I` child | Build per test | One build failure errors the class |
| [D13](#d13) | How the slowdown is evidenced | Double fold with `black_box` | Sleep or spin | Evidence of noise kept as well |
| [D14](#d14) | Test design | Real subprocesses, one test per requirement | Import `main()` or one big test | A process per test |

## <a id="d1"></a>D1: When maturin enables `extension-module`

**Chosen:** `[tool.maturin] features` · **Where:** [`rust/swarm-core/python/pyproject.toml:11-14`](../../../rust/swarm-core/python/pyproject.toml#L11-L14) · **Source:** K12

| Option | For | Against |
| --- | --- | --- |
| ✅ `[tool.maturin] features` | Workspace clippy and test never see the feature, so nothing links without libpython | A bare `cargo build` of the cdylib links libpython |
| Feature on the pyo3 dependency in [`Cargo.toml`](../../../rust/swarm-core/python/Cargo.toml) | One place | Clippy and test of the workspace then fail to link |
| A crate feature that maturin enables | Explicit name | One more feature to keep in step |
| `PYO3_BUILD_EXTENSION_MODULE` set by recent maturin | No setting | Depends on the maturin version |

**Trade-off:** development builds link libpython, which is fine. **Revisit when:** the bindings crate gets Rust tests.

## <a id="d2"></a>D2: Avoiding the build race under xdist

**Chosen:** one `--target-dir` per worker · **Where:** [`tests/rust/swarm_core/helpers.py:18-31`](../../../tests/rust/swarm_core/helpers.py#L18-L31) · **Source:** K05, review round 3

| Option | For | Against |
| --- | --- | --- |
| ✅ Target folder per `PYTEST_XDIST_WORKER` | No race, no extra dependency, cache kept between runs | One full compile per worker the first time |
| A file lock around the build | One compile | An extra dependency or hand-made locking |
| Session fixture with a shared temporary target | One compile | Named by the worker, not chosen |
| Build once on the controller | One compile | Named by the worker, not chosen |

**Trade-off:** disk and a first compile per worker, for a fix that made three `-n 2` runs pass ([run 1](tests-evidences/pytest-n2-run1.txt)). **Revisit when:** the compile time shows in CI.

## <a id="d3"></a>D3: Audit of the wheel

**Chosen:** `skip-auditwheel = true` · **Where:** [`rust/swarm-core/python/pyproject.toml:14`](../../../rust/swarm-core/python/pyproject.toml#L14) · **Source:** K12

| Option | For | Against |
| --- | --- | --- |
| ✅ Skip the audit | Cut the failure rate of the `-n 2` wheel tests from about 3 in 4 runs to about 1 in 4 (K12's figures) | The wheel loses the manylinux compliance check |
| Keep the audit | Checks compliance | Failed often under xdist |
| Fix the race in the tests | Real fix | Outside K12's files |

**Trade-off:** the cause was a race, since fixed by [D2](#d2), so this setting is now probably unneeded. **Revisit when:** at once, it is a follow-up. Whether the audit is still needed is an open point.

## <a id="d4"></a>D4: Tests of the bindings crate

**Chosen:** `test = false` and `doctest = false` · **Where:** [`rust/swarm-core/python/Cargo.toml:11-16`](../../../rust/swarm-core/python/Cargo.toml#L11-L16) · **Source:** K12

| Option | For | Against |
| --- | --- | --- |
| ✅ Switch Rust tests off | `cargo test --workspace` stays portable | No Rust unit tests here, the wheel tests cover it |
| `auto-initialize` feature | Rust tests possible | Needs libpython at test time |
| Exclude the crate from the workspace test run | Keeps tests | The crate leaves `--workspace` |

**Trade-off:** coverage moves to Python. **Revisit when:** the bindings hold logic of their own.

## <a id="d5"></a>D5: Passing data and the GIL

**Chosen:** `Vec<u64>` by value, `py.detach` · **Where:** [`rust/swarm-core/python/src/lib.rs:12-15`](../../../rust/swarm-core/python/src/lib.rs#L12-L15) · **Source:** K12

| Option | For | Against |
| --- | --- | --- |
| ✅ `Vec<u64>` with `py.detach` | Follows the engine page (GIL released) and the brief | One copy of the input |
| `&[u64]` with the GIL held | No copy | Holds the GIL |
| `PyBackedBytes` or a buffer | Zero copy | More API for a placeholder |

**Trade-off:** a copy that is acceptable for placeholders. **Revisit when:** the real logic arrives and inputs are large.

## <a id="d6"></a>D6: What the gate compares

**Chosen:** `mean.point_estimate` above 0.05 · **Where:** [`.github/scripts/bench_gate.py:136-143`](../../../.github/scripts/bench_gate.py#L136-L143) · **Source:** plan, [load tests page](../../specs/technical/07-scalability.md#load-tests)

| Option | For | Against |
| --- | --- | --- |
| ✅ Point estimate | Simple, exactly "more than 5 %" | [Evidence](tests-evidences/bench-gate-slowdown.txt) shows +12.15 % on identical code |
| Lower bound of the confidence interval | Fewer false failures | Not in the spec wording, named in review |
| Failure only if a rerun shows it too | Fewer false failures | Longer CI |

**Trade-off:** shared runners can fail a pull request for no reason. **Revisit when:** a flaky failure is seen on a real pull request.

## <a id="d7"></a>D7: Parsing and errors of the gate script

**Chosen:** manual parsing, `ValueError`, exit 2 · **Where:** [`.github/scripts/bench_gate.py:48-72`](../../../.github/scripts/bench_gate.py#L48-L72) and [`bench_gate.py:114-132`](../../../.github/scripts/bench_gate.py#L114-L132) · **Source:** K10

| Option | For | Against |
| --- | --- | --- |
| ✅ Own loop and `ValueError` | Exact messages, one class-free file | A small manual loop |
| `argparse` | Standard, exits 2 itself | Messages not exact |
| A custom exception | Specific | A class in the file breaks the one-class rule |

`Path.rglob("change/estimates.json")` ([`bench_gate.py:108`](../../../.github/scripts/bench_gate.py#L108)) was chosen over `os.walk` as shorter, with POSIX ids and any nesting depth.

**Trade-off:** more code than `argparse`. **Revisit when:** the script gets more options.

## <a id="d8"></a>D8: The baseline

**Chosen:** worktree of the base SHA, baseline `pr-base` · **Where:** [`.github/workflows/rust.yml:52-63`](../../../.github/workflows/rust.yml#L52-L63) · **Source:** plan, [TICKET.md](TICKET.md) assumptions

| Option | For | Against |
| --- | --- | --- |
| ✅ Benchmark the base commit in the same job | Same machine for both runs, no stored data | Benchmarks run twice |
| Stored results | One run | Not specified, and runners differ |

The existence test uses `compgen -G` over crate-level and root `benches` folders ([`rust.yml:55-56`](../../../.github/workflows/rust.yml#L55-L56)), because benches live in each crate. **Trade-off:** twice the CI time. **Revisit when:** the benchmarks get slow.

## <a id="d9"></a>D9: Flag order of the base run

**Chosen:** `--locked --workspace` · **Where:** [`.github/workflows/rust.yml:58`](../../../.github/workflows/rust.yml#L58) · **Source:** K11

| Option | For | Against |
| --- | --- | --- |
| ✅ Swapped order | The workflow test finds the PR step first | Looks odd |
| Brief's `--workspace --locked` | As briefed | Matches first in the test and fails it |

**Trade-off:** a test depends on flag order, a follow-up. **Revisit when:** the test looks for `--baseline-lenient pr-base`.

## <a id="d10"></a>D10: Shared dependency versions and member order

**Chosen:** `criterion` 0.8.2 and `pyo3` 0.30.1 in `[workspace.dependencies]`, members in alphabetical order · **Where:** [`rust/Cargo.toml:3-17`](../../../rust/Cargo.toml#L3-L17) · **Source:** K09, K12

| Option | For | Against |
| --- | --- | --- |
| ✅ Workspace dependencies | One version and one lock entry | All crates move together |
| Per crate | Independent | Versions can drift |
| Older criterion 0.5.x | Named by K09 | No reason given |

Alphabetical members give a stable order and a larger diff on the members line. **Revisit when:** a crate needs another version.

## <a id="d11"></a>D11: Placeholder body

**Chosen:** `fold` with `wrapping_add` · **Where:** [`rust/swarm-core/safety/src/lib.rs:10-12`](../../../rust/swarm-core/safety/src/lib.rs#L10-L12) · **Source:** K09

| Option | For | Against |
| --- | --- | --- |
| ✅ `fold` and `wrapping_add` | No allocation, no panic in any profile | Not explicitly vectorised |
| `iter().sum()` | Short | Panics on overflow in debug builds |

No `#![allow(missing_docs)]` was added to the benches: the `//!` line at [`safety/benches/tick.rs:1`](../../../rust/swarm-core/safety/benches/tick.rs#L1) is enough for clippy. **Revisit when:** the real logic replaces the placeholder.

## <a id="d12"></a>D12: Wheel test structure

**Chosen:** one class-scoped fixture, child run with `-I` · **Where:** [`tests/rust/swarm_core/test_swarm_core_wheel.py:15-20`](../../../tests/rust/swarm_core/test_swarm_core_wheel.py#L15-L20) and [`helpers.py:70-71`](../../../tests/rust/swarm_core/helpers.py#L70-L71) · **Source:** K05

| Option | For | Against |
| --- | --- | --- |
| ✅ Class-scoped fixture | One build, fast | One build failure errors every test, and the instance method triggers a pytest deprecation |
| Build per test | Isolation | Slow |
| Module-scoped fixture | Same speed | Not chosen, no reason given |
| Plain `python -c` | Simple | Might import from the cwd or the source tree, `-I` guarantees the venv |

**Revisit when:** pytest 10, see follow-ups.

## <a id="d13"></a>D13: Evidence of the gate

**Chosen:** double fold with `black_box` per element, noisy run kept · **Where:** [`tests-evidences/bench-gate-slowdown.txt`](tests-evidences/bench-gate-slowdown.txt) · **Source:** K13

| Option | For | Against |
| --- | --- | --- |
| ✅ Double fold with `black_box` | Real work, +545 %, well above 5 % | Needs the optimiser held back |
| Sleep or spin | Easy | Not real work |
| Double fold without per-element `black_box` | Simple | The optimiser can remove it |

Both the failed unchanged run and the passing rerun are recorded, rather than raising the threshold, and `lib.rs` was restored from a saved copy since it was untracked. **Trade-off:** a less tidy file for honest evidence.

## <a id="d14"></a>D14: Shape of the Python tests

**Chosen:** real subprocesses, sentence-named tests, module-level helpers · **Where:** [`tests/ci/bench_gate/helpers.py:10-43`](../../../tests/ci/bench_gate/helpers.py#L10-L43), [`tests/ci/bench_gate/test_bench_gate.py:87`](../../../tests/ci/bench_gate/test_bench_gate.py#L87), [`tests/ci/workflows/checks/test_rust_workflow.py:32-63`](../../../tests/ci/workflows/checks/test_rust_workflow.py#L32-L63) · **Source:** K04, K06, K07 (and K01 for Rust)

| Option | For | Against |
| --- | --- | --- |
| ✅ Real runs of the script, module-level helpers | Real exit codes, no mocks, matches [`tests/ci/detect_changes/helpers.py`](../../../tests/ci/detect_changes/helpers.py) | A process start per test |
| Import `main()` or mock the file system | Faster | Breaks the no-mock rule |
| Parametrise existing workflow helpers by job | Less duplication | Touches the check tests |
| One test per workflow requirement | A failure names the requirement | More methods |

Smaller choices of the same kind: a `{dir}` placeholder in one parametrised exit-2 test ([`test_bench_gate.py:77`](../../../tests/ci/bench_gate/test_bench_gate.py#L77)); one parametrised test per concern with `_load`, `_table`, `_members` helpers ([`test_swarm_core_layout.py:33-45`](../../../tests/rust/swarm_core/test_swarm_core_layout.py#L33-L45)); "bindings" in every bindings test name so `-k 'not bindings'` works ([`test_swarm_core_layout.py:91-127`](../../../tests/rust/swarm_core/test_swarm_core_layout.py#L91-L127)); `fnmatch` on the uv members ([`test_swarm_core_layout.py:127-132`](../../../tests/rust/swarm_core/test_swarm_core_layout.py#L127-L132)); and one determinism test in [`safety/tests/tick.rs`](../../../rust/swarm-core/safety/tests/tick.rs). **Revisit when:** the test run time grows.

## 📝 Assumptions behind the choices

None.
