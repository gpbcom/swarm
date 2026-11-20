# T0.06: Review note

**Verdict:** ✅ Approved · **Branch:** `ticket/T0.06`

## What changed

- A shared package, `swarm-models`, holds the first versions of nine models: Operator, CellAssignment, Person, Role, Actor, Event, TelemetryFrame, SquadFrame and Command. Every field rejects bad input with its own `SE...` exception. Identifiers must be UUIDv7 and datetimes must carry a time zone (stored in UTC). Events, frames and commands are frozen.
- One canonical JSON Schema bundle (`schemas/swarm_models.schema.json`) is exported from the models by `swarm-models-schemas`. This command goes through the storage, service and api layers inside the package, and `--check` fails when the committed bundle is stale.
- The Rust structs are generated from the bundle with typify (`swarm-models-codegen`) into the `swarm-models` crate. The TypeScript types are generated with json-schema-to-typescript into `@swarm/live`.
- Each generated file has its own stale check: the python.yml `packages` job for the bundle, a cargo test for Rust, and the `test` script for TypeScript. Any change under `packages/` triggers all three.
- AGENT.md documents where the shared models live, the three regeneration commands and the three CI checks.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given each model of the ticket, when its tests run, then it has the six model tests of AGENT.md | All nine model test files (`packages/python/swarm-models/tests/models/*/test_*.py`) have `test_defaults`, `test_full_valid_construction`, `test_none_becomes_the_default`, `test_rejects_bad_values`, `test_rejects_unknown_keys` and `test_round_trip`. `tests-evidences/pytest.txt` shows 1213 passed | ✅ Pass |
| 2. Given a stale generated file (JSON Schema, Rust or TypeScript), when CI runs, then it fails | JSON Schema: `test_check_fails_after_the_file_was_changed` and `test_the_committed_bundle_is_up_to_date`, plus the python.yml step tested by `test_the_packages_job_runs_its_checks_in_order` (`pytest.txt`). Rust: `the_generated_structs_are_current` and `an_edited_output_is_stale_again` (`cargo-test.txt`). TypeScript: "is stale again after the output is edited" and `generate.ts --check` (`test.txt`) | ✅ Pass |

## Look at first

- **Operator isolation in the envelope:** Event requires `operator_id` (UUIDv7), and `mission_id` is optional only for fleet events. Check that this fits the `op.<operator_id>.…` subjects: `models/events/event.py`.
- **Identity:** Actor's kind rules (a Person has a person_id and no agent name, a Swarm agent has an agent name, an Outside agent has both). Role's rule that `operator_id` is None exactly for a Swarm administrator. Person's `operator_id` is optional, and nothing yet checks it against the person's Roles. Files: `models/events/actor.py`, `models/people/role.py`, `models/people/person.py`.
- **Safety lane:** Command refuses a safety kind on the normal lane. Because CommandKind holds only safety kinds today, the normal lane has no kind yet. File: `models/commands/command.py`.
- **Wrong glossary meaning:** the Operator docstring calls an Operator "a person who pilots drones" instead of an organisation. The text is copied into the bundle, `generated.rs` and `models.ts` (follow-up). Files: `models/operators/operator.py`, `models/commands/enums/command_kind.py`.
- **Generation chain:** models → bundle → Rust and TypeScript. The bundle path is hard-coded relative to the source tree in all three generators. Files: `service/schemas/schema_exporter.py`, `storage/schemas/schema_folder.py`, `packages/rust/swarm-models-codegen/src/lib.rs`, `packages/ts/live/scripts/generate.ts`.
- **Outside the ticket's scope:** the branch also carries the person's harness commit `05a8f48` (`.claude/`, `tests/harness/`). It was not reviewed against TICKET.md, and it merges into `develop` with the ticket.
- **Simulator isolation:** not touched.

## Assumptions accepted

- No FS, UC or BR to cite: accepted, the roadmap row names none.
- Proposal is not built: accepted, the roadmap lists Event only.
- Conservative fields for Operator, Person, Role and CellAssignment, with Role's `operator_id` None for a Swarm administrator: accepted, consistent with 06-security#authorisation.
- The stale checks reuse the T0.04 workflows: accepted, since a change under packages/ selects every job.
- No `payload_state` yet: accepted, the glossary has no Payload state, and the field can be added later without breaking the version.
- DroneState has the six glossary states: accepted.
- SquadFrame holds full frames, without delta encoding: accepted, delta encoding belongs to the wire format of the live path.
- CommandKind has only the four safety kinds, and a safety kind is refused on the normal lane: accepted.
- Event's type pattern, version of at least 1, optional `mission_id`, and Actor kinds: accepted, they follow #events.

## Follow-ups

- Rewrite the Operator docstring and the MANUAL_CONTROL docstring with the glossary meanings (Operator is an organisation, the Pilot takes manual control), then regenerate the bundle, the Rust structs and the TypeScript types.
- Put one sentence per source line in the two-sentence messages (AGENT.md Messages), and fix the range text shown when the maximum is excluded.
- Declare the TelemetryFrame bounds with `Field(ge/le/lt)` too, so the JSON Schema, Rust and TypeScript carry them.
- Shorten the descriptions copied into the schema and drop the field titles, so the TypeScript output has no duplicate aliases (`Id1`, `ActorKind1` and so on).
- Add the missing `Raises:` sections to the Command, Person and Role validators.
- Make `SchemaFolder.DEFAULT_ROOT` independent of the source layout if the package is ever installed as a wheel.
- Measure TelemetryFrame validation against the budgets when frames enter the live path (T0.18, T0.19).
