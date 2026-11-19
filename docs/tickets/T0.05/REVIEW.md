# T0.05: Review note

**Verdict:** ✅ Approved · **Branch:** `ticket/T0.05`

## What changed

- Three shared uv workspace packages under `packages/python/`:
  - `swarm-lifecycle`: `Runnable`, `AsyncRunnable`, and the factories `Factory[T]`, `RunnableFactory` and `AsyncRunnableFactory`. Callers use `create()` and subclasses implement `_build()`.
  - `swarm-logging`: `ColouredFormatter`, `JsonFormatter`, the `LoggingConfig` model and `LoggingConfigurator`, plus a reference `logger.yaml` (coloured console on stderr, coloured rotating `logs/swarm.log`, root level DEBUG).
  - `swarm-catalog`: the frozen `YamlCatalog` with `load(path)`, which raises the subclass's `UNREADABLE`.
- `execute()` always closes in a `finally` and catches nothing. It logs INFO with the duration on success and ERROR when the work fails. The original error goes up unchanged.
- JSON in production comes from `LoggingConfig.format = json`. In that mode every formatter of the file becomes `JsonFormatter`: one JSON object per line, in UTC, with no colour codes.
- The gateway now uses the packages. `main()` configures logging, builds `GreetingCommand` (a `Command(Runnable)`) through `GreetingCommandFactory`, and executes it. The output is still `Hello from swarm!`.
- The convention tests now also run against every package of `packages/python/`. The lifecycle rule accepts the definitions of `Runnable` and `AsyncRunnable` themselves. AGENT.md and the README now say where each base class lives.

## Acceptance criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| 1. Given the service skeletons of P0, when they are built, then every one uses the lifecycle and logging packages | `services/gateway/tests/api/cli/test_main.py` (`test_main_gives_the_root_logger_a_rotating_file_handler`, `test_main_writes_the_log_file_under_the_current_folder`), `test_greeting_command_factory.py`, `tests-evidences/pytest.txt` | ✅ Pass (only the gateway exists today) |
| 2. Given the packages, when their own tests run, then they pass | `tests-evidences/pytest.txt` (644 passed), `tests-evidences/mypy.txt`, `ruff-check.txt`, `ruff-format.txt` | ✅ Pass |
| 3. Given the packages, when the convention tests of `tests/conventions/` run, then they accept them | `tests/conventions/packages/test_package_conventions.py::test_every_rule_holds_for_every_package`, `tests-evidences/pytest.txt` | ✅ Pass |

## Look at first

- **The lifecycle contract**, which every future service inherits: the close-in-`finally` order, the success flag, and that errors are never swallowed. Files: `packages/python/swarm-lifecycle/src/swarm_lifecycle/runnables/runnable.py`, `async_runnable.py`.
- **The factory shape:** `create()` logs and `_build()` is abstract, with PEP 695 generics. Files: `packages/python/swarm-lifecycle/src/swarm_lifecycle/factories/factory.py`, `services/gateway/src/gateway/api/factories/`.
- **How JSON in production is chosen:**
  - In the package, by `LoggingConfig.format`, with the formatter swap in `_apply_format`. File: `packages/python/swarm-logging/src/swarm_logging/configurators/logging_configurator.py`.
  - The gateway hard-codes the coloured default for now. File: `services/gateway/src/gateway/api/cli/main.py`.
- **The convention exemption by class name.** File: `tests/conventions/rules/classes/lifecycle_base_classes.py`.
- **Identity, Operator isolation and Simulator isolation:** not touched by this ticket. No secret appears in code or logs: the configurator logs only `type(error).__name__` on failure.

## Assumptions accepted

- No feature, use case or business rule is cited: accepted, because the roadmap row names none.
- Criterion 1 is checked on the gateway only: accepted, because the other skeletons belong to T0.12.
- JSON is selected by `LoggingConfig.format`, set by the deployment: accepted, because the specifications are silent and this is the conservative choice.
- K17 and K20, ABC listed explicitly on the abstract factories: accepted, because nothing changes at runtime.
- K18, `JSON_FORMATTER` as a ClassVar: accepted, because it follows the AGENT.md constant rule.
- K18, `noqa: E501` dropped because of RUF100: accepted, because keeping it would break ruff. The message should still be split (see the follow-ups).
- K18, a file with no formatters is left as it is in JSON mode: accepted for now, because every current file has formatters. See the follow-ups.

## Follow-ups

- Gateway (K20): read `LoggingConfig` from `conf/app.yaml` when T0.12 adds it, so that production can switch to JSON.
- Configurator (K18): in JSON mode, also give JSON to handlers whose file declares no formatter.
- Messages (K13, K18): split the two-sentence messages into one sentence per line, and settle the conflict between the AGENT.md `noqa: E501` rule and RUF100.
- `YamlCatalog.load` (K13): decide whether a schema mismatch should raise `UNREADABLE` rather than pydantic's `ValidationError`.
- Lifecycle rule (K16): limit the name-based exemption to `swarm_lifecycle`, and update its stale Note.
- Test stand-ins (K01, K02): remove the import group comments.
