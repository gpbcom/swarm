# T0.06: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- Every model has the six model tests of AGENT.md, and a stale JSON Schema, Rust or TypeScript file makes CI fail ([TICKET.md](TICKET.md)).
- One class per file, at most five Python files per folder, no `Any`, no module-level code, models only validate and never log (AGENT.md).
- `api` never imports `storage`, so the export goes through a service layer (AGENT.md Layout).
- Shared code lives in `packages/` and holds no business rules (AGENT.md Mono-repo).
- Frames and events are frozen, identifiers are UUIDv7 and time is UTC ([02-data-models](../../specs/technical/02-data-models.md#conventions)).
- The specification names Operator, Person, Role, CellAssignment and SquadFrame without their fields ([02-data-models](../../specs/technical/02-data-models.md#models)).
- T0.04 workflows already exist and select every job on a change under `packages/`.

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | Source of the generated types | Pydantic models, one JSON Schema bundle, Rust and TypeScript generated from it | Hand-written types per language | A three-step regeneration chain, and the Python docstrings leak into every language |
| [D2](#d2) | Where the stale checks run | Reuse the T0.04 workflows: a `packages` job, a cargo test, the `test` script | A new dedicated CI workflow | Checks hide inside test commands |
| [D3](#d3) | Field sets of the models the specification does not detail | The most conservative set | Richer sets guessed from the product | Later tickets add fields |
| [D4](#d4) | Safety lane | Only four safety kinds, a safety kind on the normal lane is refused | Also model the normal kinds now | The normal lane has no kind yet |
| [D5](#d5) | Validation style | Own exception per field, base helpers, `mode="before"` validators | Pydantic `Field(ge, le)` constraints | Bounds are absent from the generated types |
| [D6](#d6) | SquadFrame content | Full TelemetryFrames | Delta against the previous tick | Larger frames until the wire format exists |
| [D7](#d7) | Event envelope | `mission_id` optional, Outside agent carries agent and person | Required `mission_id` | A fleet event has no Mission, so the model allows None for every event |
| [D8](#d8) | Rust generation | A separate codegen crate with typify as a library | A build script in the models crate | A second crate to maintain |
| [D9](#d9) | Bundle path | Hard-coded relative to the source tree | Explicit root or package data | Does not work from a wheel |

## <a id="d1"></a>D1: Source of the generated types

**Chosen:** the Pydantic models are the source, exported as one canonical bundle · **Where:** [`packages/python/swarm-models/src/swarm_models/service/schemas/schema_exporter.py:77`](../../../packages/python/swarm-models/src/swarm_models/service/schemas/schema_exporter.py#L77) · **Source:** PLAN.md assumption 17

| Option | For | Against |
| --- | --- | --- |
| ✅ One bundle for the nine models | Rust and TypeScript share one set of type names. The bundle is sorted and ends with one newline, so a stale check is a text comparison | Docstrings and field titles are copied into it, giving duplicate TypeScript aliases (see follow-ups) |
| One schema file per model | Smaller files | Shared types such as the Actor would be defined once per file |
| Hand-written types in each language | No generator to maintain | Nothing would fail on drift, and acceptance criterion 2 asks for a failing check |

**Trade-off:** the chain models, bundle, Rust and TypeScript has three regeneration commands, in exchange for one source of truth.

**Revisit when:** the duplicate TypeScript aliases hurt the consumers, which is the first follow-up on schema descriptions.

## <a id="d2"></a>D2: Where the stale checks run

**Chosen:** reuse the existing workflows · **Where:** [`python.yml:81`](../../../.github/workflows/python.yml#L81), [`generated_is_current.rs:6`](../../../packages/rust/swarm-models/tests/generated_is_current.rs#L6), [`package.json:11`](../../../packages/ts/live/package.json#L11) · **Source:** PLAN.md assumptions 18 to 20

| Option | For | Against |
| --- | --- | --- |
| ✅ Reuse T0.04 workflows | `rust.yml`, `typescript.yml`, `ci.yml` and `detect_changes.py` stay unchanged, and any change under `packages/` selects all three | A reader must know the check is inside `cargo test` and the `test` script |
| A new workflow for generated files | One visible job | More CI to keep, and T0.04 owns the job layout |

**Trade-off:** AGENT.md now documents the three checks so they are findable.

**Revisit when:** a fourth generated target appears.

## <a id="d3"></a>D3: Field sets the specification does not detail

**Chosen:** the most conservative set (TKT-8) · **Where:** [`packages/python/swarm-models/src/swarm_models/models/people/role.py:86`](../../../packages/python/swarm-models/src/swarm_models/models/people/role.py#L86) · **Source:** PLAN.md assumptions 3 and 10

| Option | For | Against |
| --- | --- | --- |
| ✅ Minimal fields | Nothing is invented. New optional fields are additive within a version ([#versioning](../../specs/technical/02-data-models.md#versioning)) | Later tickets must extend the models |
| Richer sets | Fewer later changes | Fields nobody specified would look agreed |

**Trade-off:** Role's `operator_id` is None exactly for a Swarm administrator, which follows 06-security#authorisation. Nothing yet checks a Person's `operator_id` against their Roles.

**Revisit when:** the back-office tickets need more fields.

## <a id="d4"></a>D4: Safety lane

**Chosen:** four safety kinds, and a safety kind on the normal lane is refused · **Where:** [`packages/python/swarm-models/src/swarm_models/models/commands/command.py:146`](../../../packages/python/swarm-models/src/swarm_models/models/commands/command.py#L146) · **Source:** PLAN.md assumption 16

| Option | For | Against |
| --- | --- | --- |
| ✅ Only the four named kinds | The specification names no others. The safety lane always jumps the queue, so a safety kind must not wait | The normal lane has no kind yet |
| Invent normal kinds | A complete lane model | Kinds nobody specified |

**Trade-off:** normal kinds arrive with the flight engine.

**Revisit when:** the flight engine defines them.

## <a id="d5"></a>D5: Validation style

**Chosen:** one exception per field, shared `SwarmModel` helpers, `mode="before"` validators · **Where:** [`packages/python/swarm-models/src/swarm_models/models/base/swarm_model.py:36`](../../../packages/python/swarm-models/src/swarm_models/models/base/swarm_model.py#L36) · **Source:** PLAN.md assumptions 7 and 8, review

| Option | For | Against |
| --- | --- | --- |
| ✅ Own exception and before-validators | AGENT.md requires a validator and an exception per field, and bool is refused for numbers | The bounds are not in the JSON Schema, and before-validators skip pydantic-core's fast path |
| `Field(ge, le, lt)` only | The bounds reach Rust and TypeScript | Breaks the per-field exception rule alone |

**Trade-off:** the reviewer asked, as a follow-up, to declare the bounds with `Field` as well. No budget applies yet to the speed of validation, and nobody has measured it.

**Revisit when:** frames enter the live path (T0.18, T0.19).

## <a id="d6"></a>D6: SquadFrame content

**Chosen:** full frames · **Where:** [`packages/python/swarm-models/src/swarm_models/models/telemetry/squad_frame.py:97`](../../../packages/python/swarm-models/src/swarm_models/models/telemetry/squad_frame.py#L97) · **Source:** PLAN.md assumption 15

| Option | For | Against |
| --- | --- | --- |
| ✅ Full TelemetryFrames | Simple to validate and to reason about | Larger than a delta |
| Delta against the previous tick | Smaller on the wire | A wire concern of the live path, not of the model |

**Trade-off:** size is deferred.

**Revisit when:** T0.18, T0.19 or P1 set the wire encoding.

## <a id="d7"></a>D7: Event envelope

**Chosen:** `operator_id` required, `mission_id` optional · **Where:** [`packages/python/swarm-models/src/swarm_models/models/events/event.py:27`](../../../packages/python/swarm-models/src/swarm_models/models/events/event.py#L27) · **Source:** PLAN.md assumption 11

| Option | For | Against |
| --- | --- | --- |
| ✅ Optional `mission_id` | The fleet subject `op.<operator_id>.fleet.<event>` has no Mission | A mission event without a Mission is not refused by the model |
| Required `mission_id` | Stricter | Cannot carry fleet events |

**Trade-off:** the model cannot tell a fleet event from a mission event.

**Revisit when:** the event types are listed.

## <a id="d8"></a>D8: Rust generation

**Chosen:** a separate `swarm-models-codegen` crate · **Where:** [`packages/rust/swarm-models-codegen/src/lib.rs:49`](../../../packages/rust/swarm-models-codegen/src/lib.rs#L49) · **Source:** PLAN.md assumption 18

| Option | For | Against |
| --- | --- | --- |
| ✅ Codegen crate, committed `generated.rs` | The file is reviewable, and the stale check is a cargo test | A second crate |
| Build script | Never stale | Hides the output, and the build needs the bundle and typify |

**Trade-off:** a committed generated file must be regenerated by hand.

**Revisit when:** the regeneration step becomes a burden.

## <a id="d9"></a>D9: Bundle path

**Chosen:** `DEFAULT_ROOT` relative to the source tree · **Where:** [`packages/python/swarm-models/src/swarm_models/storage/schemas/schema_folder.py:25`](../../../packages/python/swarm-models/src/swarm_models/storage/schemas/schema_folder.py#L25) · **Source:** read from the diff, review

| Option | For | Against |
| --- | --- | --- |
| ✅ Path from `__file__` | Works in the workspace and for the three generators | Fails if the package is installed as a wheel |
| Explicit root or package data | Works everywhere | More configuration. The reason it was not chosen is not recorded |

**Trade-off:** accepted while the package is only used from the workspace.

**Revisit when:** the package is installed as a wheel.

## 📝 Assumptions behind the choices

- No FS, UC or BR to cite: supports [D1](#d1).
- Conservative fields for Operator, Person, Role and CellAssignment: supports [D3](#d3).
- Stale checks reuse the T0.04 workflows: supports [D2](#d2).
- CommandKind has four safety kinds only: supports [D4](#d4).
- SquadFrame holds full frames: supports [D6](#d6).
- Event type pattern, optional `mission_id`, Actor kinds: supports [D7](#d7).
- SwarmModel base and one exception per field: supports [D5](#d5).
