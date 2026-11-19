# T0.05: Lifecycle and logging packages

**Status:** ✅ Done · **Roadmap:** [T0.05](../../specs/roadmap/01-p0-foundations.md#s01) in [🛣️ P0: Foundations](../../specs/roadmap/01-p0-foundations.md) · **Ticket:** [TICKET.md](TICKET.md)

## 🔭 What changed for users

- Nothing a user of the gateway sees changes: the command still prints `Hello from swarm!`.
- The gateway now writes its logs through the shared logging package: coloured on the console, and in a coloured rotating file `logs/swarm.log`.
- JSON logs are available in the package, selected by `LoggingConfig.format = json`. The gateway does not yet read that setting, so in the gateway the logs stay coloured (see the follow-ups).

## 🧱 What changed in the code

The diff is `develop~1...develop`, 77 files, merged from `ticket/T0.05`.

- **`packages/python/swarm-lifecycle`** (`swarm_lifecycle`):
  - `Runnable` and `AsyncRunnable`, with `initialize()`, `run()`, `close()` and `execute()`. `execute()` always closes in a `finally` and catches nothing. It logs INFO with the duration on success and ERROR when the work fails. The original error goes up unchanged.
  - The factories `Factory[T]`, `RunnableFactory` and `AsyncRunnableFactory`. Callers use `create()`, which logs, and subclasses implement the abstract `_build()`. PEP 695 generics are used.
- **`packages/python/swarm-logging`** (`swarm_logging`):
  - `ColouredFormatter` and `JsonFormatter`. JSON output is one object per line, in UTC, with no colour codes.
  - The `LoggingConfig` model, with `format` (coloured or json), and `LoggingConfigurator`. In JSON mode every formatter of the file becomes `JsonFormatter`.
  - A reference `conf/logger.yaml`: coloured console on stderr, coloured rotating `logs/swarm.log`, root level DEBUG.
  - The configurator logs only `type(error).__name__` on failure, so no secret or typed value reaches the log.
- **`packages/python/swarm-catalog`** (`swarm_catalog`): the frozen `YamlCatalog` with `load(path)`, which raises the subclass's `UNREADABLE` exception.
- **`services/gateway`**:
  - `main()` configures logging, builds `GreetingCommand` (a `Command(Runnable)`) through `GreetingCommandFactory`, and executes it.
  - `api/factories/` holds the `CommandFactory` and the `GreetingCommandFactory`.
- **Conventions and documentation**:
  - The convention tests now also run against every package of `packages/python/` (`tests/conventions/packages/test_package_conventions.py`).
  - The lifecycle rule accepts the definitions of `Runnable` and `AsyncRunnable` themselves (`tests/conventions/rules/classes/lifecycle_base_classes.py`).
  - AGENT.md and the README now say where each base class lives.
  - `uv.lock` records the three new workspace packages.

## 🧪 How to test it

From the repository root:

```bash
uv sync
uv run pytest packages/python/swarm-lifecycle/tests -n 2
uv run pytest packages/python/swarm-logging/tests -n 2
uv run pytest packages/python/swarm-catalog/tests -n 2
uv run pytest services/gateway/tests -n 2
uv run pytest tests/conventions/packages -n 2
uv run ruff check packages services tests
uv run mypy packages/python/swarm-lifecycle/src packages/python/swarm-logging/src packages/python/swarm-catalog/src services/gateway/src
```

Run the tests one folder at a time if the parallel run is not stable on your machine.

To see JSON output, set `format: json` in the `LoggingConfig` used by a test or a script, then read the file with `tail -f`.

## 🔗 Evidence

- [Pytest output](tests-evidences/pytest.txt): 644 passed.
- [Mypy output](tests-evidences/mypy.txt).
- [Ruff check](tests-evidences/ruff-check.txt) and [ruff format](tests-evidences/ruff-format.txt).
- [Specifications check](tests-evidences/specs-check.txt) and [ticket references](tests-evidences/ticket-refs.txt).
- [Review note](REVIEW.md): ✅ Approved, 0 blocking findings, 6 follow-ups.
- [Progress and events](PROGRESS.md).

## ✅ Acceptance criteria

| Criterion | Result |
| --- | --- |
| 1. Given the service skeletons of P0, when they are built, then every one uses the lifecycle and logging packages | ✅ Pass for the gateway, the only skeleton that exists today. The other skeletons belong to T0.12. |
| 2. Given the packages, when their own tests run, then they pass | ✅ Pass (644 passed, see the pytest evidence) |
| 3. Given the packages, when the convention tests of `tests/conventions/` run, then they accept them | ✅ Pass (`test_every_rule_holds_for_every_package`) |

The roadmap row names no feature, use case or business rule, so the criteria cite none.

## 📌 Out of scope

- The service skeletons that use the packages: [T0.12](../../specs/roadmap/01-p0-foundations.md#s03).
- The shared models and the `Event` envelope: [T0.06](../../specs/roadmap/01-p0-foundations.md#s02).
- The shared async NATS client: [T0.09](../../specs/roadmap/01-p0-foundations.md#s02).
- OpenTelemetry and the observability stack: [T0.17](../../specs/roadmap/01-p0-foundations.md#s04).

Identity, Operator isolation and Simulator isolation are not touched by this ticket.

## ⚠️ Assumptions accepted by the reviewer

- No feature, use case or business rule is cited: accepted, because the roadmap row names none.
- Criterion 1 is checked on the gateway only: accepted, because the other skeletons are T0.12, which is out of scope.
- `YamlCatalog` and the factories behave as AGENT.md describes: accepted, because AGENT.md is the only source that describes them.
- JSON is selected by `LoggingConfig.format`, set by the deployment, and the package reads no environment variable: accepted, because it is conservative and the specifications are silent. The gateway's wiring is a follow-up for T0.12.
- K17 and K20, ABC listed explicitly on the abstract factories: accepted, because nothing changes at runtime and the abstract intent is explicit.
- K18, `JSON_FORMATTER` as a ClassVar holding the JSON formatter dotted path: accepted, because AGENT.md wants constants as `UPPER_CASE` ClassVars.
- K18, `# noqa: E501` dropped because ruff flags it as RUF100: accepted, because keeping it would break `ruff check`. The message should still be split (follow-up).
- K18, in JSON mode a file with no formatters section is left as it is: accepted for now, because the reference `logger.yaml` and every current caller have formatters. Making it always JSON is a follow-up.

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| `services/gateway/src/gateway/api/cli/main.py` | `main()` hard-codes `LoggingConfig()`, so the gateway always logs in coloured format and has no way to switch to JSON in production. When T0.12 adds the gateway's `conf/app.yaml`, read `LoggingConfig` (path and format) from it. Until then, this gap stays open. |
| `packages/python/swarm-logging/src/swarm_logging/configurators/logging_configurator.py` | In JSON mode, a configuration file with no formatters section keeps the default text formatter, so production logs from that file would not be JSON. Add the JSON formatter and assign it to every handler instead of leaving the file as it is. |
| `packages/python/swarm-logging/src/swarm_logging/configurators/logging_configurator.py` | The messages `Invalid logging configuration {path!r}. Must be a mapping.` (`_read`) and `Unreadable catalog: {path}. Must be a YAML mapping in UTF-8.` (`swarm_catalog/models/yaml_catalog.py` `load`) put two sentences on one source line. Split them into one sentence per line. Also settle the conflict between AGENT.md's `# noqa: E501` instruction and ruff's RUF100: either enable E501 or change the rule in AGENT.md. |
| `packages/python/swarm-catalog/src/swarm_catalog/models/yaml_catalog.py` | When the YAML content does not match the model, `load()` raises pydantic's `ValidationError`, not `UNREADABLE` (the test `test_an_unknown_key_is_refused` covers this). Decide whether a schema mismatch should also raise `UNREADABLE`, and write the decision in the docstring. |
| `tests/conventions/rules/classes/lifecycle_base_classes.py` | The exemption applies to any class named `Runnable` or `AsyncRunnable` in any service or package, not only to `swarm_lifecycle`. Limit it to the `swarm_lifecycle` package. Also update the stale Note "The lifecycle classes arrive in a later ticket, so they are recognised by name". |
| `packages/python/swarm-lifecycle/tests/factories/runnable/lifecycle_sample_runnable_factory.py` | The test stand-in files (`lifecycle_sample_*.py` and `lifecycle_recording_*.py`) carry `# First-party imports` comments, with the bare-module import placed above that group. Remove the group comments to follow the test-file style. |
