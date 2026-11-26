# T0.06: Shared models and generated types

**Status:** ✅ Done · **Ticket:** [TICKET.md](TICKET.md) · **Choices and trade-offs:** [IMPLEMENTATION.md](IMPLEMENTATION.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🔭 What it does

- A shared Python package, `swarm-models`, holds the first versions of nine models: Operator, CellAssignment, Person, Role, Actor, Event, TelemetryFrame, SquadFrame and Command.
- Every field rejects bad input with its own exception. Identifiers must be UUIDv7 and datetimes must carry a time zone.
- One JSON Schema bundle is exported from the models, and Rust structs and TypeScript types are generated from it.
- CI fails when the bundle, the Rust file or the TypeScript file is stale.

## ⚙️ How it works

1. **Base helpers:** every model subclasses `SwarmModel`, whose classmethods check UUIDv7, UTC datetimes, text and bounded numbers, and raise the exception class each field passes in, in [`backend/swarm-models/src/swarm_models/base/swarm_model.py:36`](../../../backend/swarm-models/src/swarm_models/base/swarm_model.py#L36).
2. **Models:** each field has a `mode="before"` validator. Actor's kind rule is in [`backend/swarm-models/src/swarm_models/events/actor.py:103`](../../../backend/swarm-models/src/swarm_models/events/actor.py#L103), Event's envelope in [`backend/swarm-models/src/swarm_models/events/event.py:27`](../../../backend/swarm-models/src/swarm_models/events/event.py#L27), Role's rule that `operator_id` is None only for a Swarm administrator in [`backend/swarm-models/src/swarm_models/people/role.py:86`](../../../backend/swarm-models/src/swarm_models/people/role.py#L86), SquadFrame's one-Mission, one-frame-per-Drone rule in [`backend/swarm-models/src/swarm_models/telemetry/squad_frame.py:97`](../../../backend/swarm-models/src/swarm_models/telemetry/squad_frame.py#L97), and Command's refusal of a safety kind on the normal lane in [`backend/swarm-models/src/swarm_models/commands/command.py:146`](../../../backend/swarm-models/src/swarm_models/commands/command.py#L146).
3. **Storage:** `SchemaFolder` reads and writes the bundle file, in [`backend/swarm-storage/src/swarm_storage/shared/schemas/schema_folder.py:12`](../../../backend/swarm-storage/src/swarm_storage/shared/schemas/schema_folder.py#L12).
4. **Service:** `SchemaExporter.render` builds one bundle for the nine models with pydantic and dumps it with sorted keys, in [`backend/swarm-service/src/swarm_service/shared/schema/schema_exporter.py:77`](../../../backend/swarm-service/src/swarm_service/shared/schema/schema_exporter.py#L77). `is_stale` compares it with the file on disk, in [`backend/swarm-service/src/swarm_service/shared/schema/schema_exporter.py:98`](../../../backend/swarm-service/src/swarm_service/shared/schema/schema_exporter.py#L98).
5. **Command line:** `swarm-models-schemas [--check] [--output DIR]` writes the bundle, or exits non-zero when it is stale, in [`packages/python/swarm-models/src/swarm_models/api/cli/export_schemas.py:16`](https://github.com/gpbcom/swarm/blob/a2e43f7e74d65cc12a43507ec33f673fd2bc62e3/packages/python/swarm-models/src/swarm_models/api/cli/export_schemas.py#L16).
6. **Rust:** the codegen crate renders typify structs from the bundle, in [`rust/swarm-models-codegen/src/lib.rs:49`](../../../rust/swarm-models-codegen/src/lib.rs#L49), and writes `generated.rs`. The test [`generated_is_current.rs:6`](../../../rust/swarm-models/tests/generated_is_current.rs#L6) fails when the file is stale.
7. **TypeScript:** [`generate.ts:19`](../../../frontend/packages/live/scripts/generate.ts#L19) renders types with json-schema-to-typescript. The `test` script ends with `generate.ts --check`, in [`package.json:11`](../../../frontend/packages/live/package.json#L11).
8. **CI:** the `packages` job of [`python.yml:81`](../../../.github/workflows/python.yml#L81) runs ruff, mypy, pytest, then `swarm-models-schemas --check`. Rust and TypeScript are covered by their existing workflows.

## 🧱 Files and lines changed

<!-- changes -->
| File | Change | Lines in the new version | Added | Removed |
| --- | --- | --- | --- | --- |
| **0 files** | | | **+0** | **−0** |
<!-- /changes -->

- [`backend/libs/swarm-web/src/swarm_web/models/rest/exceptions/server/`](../../../backend/libs/swarm-web/src/swarm_web/models/rest/exceptions/server): the base, the nine models, their enums and one exception per field, grouped in five concerns (operators, people, events, telemetry, commands) plus schema errors.
- [`backend/swarm-api/src/swarm_api/v1/live`](../../../backend/swarm-api/src/swarm_api/v1/live), [`backend/swarm-api/src/swarm_api/v1/flight`](../../../backend/swarm-api/src/swarm_api/v1/flight), [`backend/libs/swarm-web/src/swarm_web/models/rest/exceptions/idempotency_key`](../../../backend/libs/swarm-web/src/swarm_web/models/rest/exceptions/idempotency_key): the three layers of the schema export.
- [`backend/swarm-models/schemas/swarm_models.schema.json`](../../../backend/swarm-models/schemas/swarm_models.schema.json): the committed bundle.
- [`packages/python/swarm-models/tests/`](https://github.com/gpbcom/swarm/blob/a2e43f7e74d65cc12a43507ec33f673fd2bc62e3/packages/python/swarm-models/tests): tests mirroring the source, with the six model tests for each model.
- [`rust/swarm-models-codegen`](../../../rust/swarm-models-codegen), [`rust/swarm-models`](../../../rust/swarm-models): the generator, the generated structs and their tests, plus workspace and lock files.
- [`frontend/packages/live`](../../../frontend/packages/live): the generator, `src/generated/models.ts`, its tests and configuration.
- [`.github/workflows/python.yml`](../../../.github/workflows/python.yml), lines 81-116: the `packages` job. [`tests/ci/workflows/checks/test_python_workflow.py`](../../../tests/ci/workflows/checks/test_python_workflow.py) goes from two jobs to three.
- [`AGENT.md`](../../../AGENT.md), lines 32-41 and 113-119: where the shared models live, the regeneration commands and the three stale checks.
- `pyproject.toml`, `uv.lock`, `pnpm-lock.yaml`: the workspace entries for the new package.
- The branch also carries the harness commit `05a8f48` (`.claude/`, `tests/harness/`), outside this ticket.

## 🧪 How to test it

```bash
uv run pytest packages/python/swarm-models/tests -n 2   # models, exporter, CLI
uv run swarm-models-schemas --check                      # bundle is current
(cd packages/rust && cargo test --workspace --locked)    # Rust structs are current
pnpm --filter @swarm/live test                           # TypeScript types are current
```

## 🔗 Evidence

- [pytest](tests-evidences/pytest.txt): 1213 passed.
- [ruff check](tests-evidences/ruff-check.txt), [ruff format](tests-evidences/ruff-format.txt), [mypy](tests-evidences/mypy.txt): clean.
- [cargo test](tests-evidences/cargo-test.txt), [cargo clippy](tests-evidences/cargo-clippy.txt), [cargo fmt](tests-evidences/cargo-fmt.txt): pass.
- [TypeScript test](tests-evidences/test.txt), [typecheck](tests-evidences/typecheck.txt), [lint](tests-evidences/lint.txt): pass.
- [specs check](tests-evidences/specs-check.txt), [ticket refs](tests-evidences/ticket-refs.txt), [plan view](tests-evidences/plan-view.txt): clean.

## 📝 Assumptions accepted

- The roadmap row names no FS, UC or BR, so the acceptance criteria cite none.
- Proposal is not built: the roadmap row lists Event, not Proposal.
- Conservative field sets for Operator (id, name), Person (id, optional operator_id, name, email), Role (person_id, optional operator_id, name) and CellAssignment (operator_id, cell, assigned_at). Role's operator_id is None exactly for a Swarm administrator, as in 06-security#authorisation.
- The stale-file checks reuse the T0.04 workflows: a python.yml `packages` job, `cargo test` and the `test` script. detect_changes.py selects all three when anything under packages/ changes.
- TelemetryFrame leaves out payload_state: the glossary names no Payload state, and adding it later is an additive change.
- DroneState has the six Drone states of the glossary, with lower-case values.
- SquadFrame holds full TelemetryFrames, not deltas. It rejects frames of another Mission and duplicate Drones.
- CommandKind holds only the four safety kinds, and a safety kind on the normal lane is refused.
- Event: type pattern after 'mission.planned', version at least 1, optional mission_id for fleet events. An Outside agent carries both the agent and the person.
- SwarmModel base with parse helpers, and one exception per field under a model base that subclasses Exception.

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| [`operator.py:15`](../../../backend/swarm-models/src/swarm_models/operators/operator.py#L15) | K19: the docstring says "A person who pilots drones", but an Operator is an organisation (ent-operator). Fix it, check `cell_assignment.py`, then regenerate the bundle, `generated.rs` and `models.ts`. |
| [`command_kind.py:17`](../../../backend/swarm-models/src/swarm_models/commands/enums/command_kind.py#L17) | K23: MANUAL_CONTROL says "Hand the control to the Operator". The Pilot takes manual control. Fix and regenerate. |
| [`swarm_model.py:58`](../../../backend/swarm-models/src/swarm_models/base/swarm_model.py#L58) | K15, K19 to K23: two-sentence messages sit on one source line. Put one sentence per line, with `# noqa: E501` on the first. |
| [`swarm_model.py:166`](../../../backend/swarm-models/src/swarm_models/base/swarm_model.py#L166) | K15: with `maximum_exclusive=True` the message still shows an inclusive range. Say the maximum is excluded. |
| [`telemetry_frame.py:85`](../../../backend/swarm-models/src/swarm_models/telemetry/telemetry_frame.py#L85) | K22: the bounds exist only in before-validators, so the schema, Rust and TypeScript carry none. Also declare them with `Field(ge, le, lt)`. |
| [`schema_exporter.py:85`](../../../backend/swarm-service/src/swarm_service/shared/schema/schema_exporter.py#L85) | K25, K28: whole class docstrings become schema descriptions, and field titles make duplicate TypeScript aliases (ActorKind1, Id1 to Id3, OperatorId1 to OperatorId3). Shorten descriptions and drop titles. |
| [`command.py:58`](../../../backend/swarm-models/src/swarm_models/commands/command.py#L58) | K23, K20: several validators in Command, Person and Role raise without a `Raises:` section. |
| [`schema_folder.py:25`](../../../backend/swarm-storage/src/swarm_storage/shared/schemas/schema_folder.py#L25) | K24: `DEFAULT_ROOT` works only from the source tree or an editable install. Pass the root or ship the bundle as package data before any wheel install. |
| [`telemetry_frame.py:96`](../../../backend/swarm-models/src/swarm_models/telemetry/telemetry_frame.py#L96) | K22: all fields use Python before-validators, which skip the fast path. Measure when frames enter the live path (T0.18, T0.19). |
