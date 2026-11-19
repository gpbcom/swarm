# CLAUDE.md

@AGENT.md

## Code rules never to break

Seven rules of [AGENT.md](AGENT.md) hold for people and agents alike, in `src/` and `tests/`:

- **No `Any` and no `object` as a type.** Both are too generic. Write the real type: `JsonValue` for parsed JSON, YAML
  or TOML, a `Union` for several known types, a `Callable[...]` with its signature, a generic with its real parameter
  (AGENT.md, Typing).
- **Every `try` has an `except`, even if only to log.** A `try` with only a `finally` is forbidden: the `except` logs at
  `ERROR` and raises again with a bare `raise` when it cannot handle the error (AGENT.md, Exceptions).
- **No dict with hard-coded keys inside a method or function.** A fixed dict is an `UPPER_CASE` `ClassVar`; when its
  values are computed, its keys are `UPPER_CASE` `ClassVar[str]` constants (AGENT.md, File shape).
- **A long-running async task ALWAYS yields its status.** Async work that can last runs in an `AsyncRunnable`, whose
  `execute()` is an async generator of `RunnableStatus` (a `StrEnum` of `swarm_lifecycle.models.enums`): `INITIALISING`
  or `RUNNING` every `status_interval_s` (required, from its configuration), then `EXECUTED` when the work succeeds
  (AGENT.md, Lifecycle and factories).
- **NO raw string in the code of `src/`.** A status, a phase, a kind, a mode, a key, a field name or an encoding is a
  `StrEnum` member in `models/enums.py` or an `UPPER_CASE` `ClassVar`. Only log, exception and `print` messages,
  docstrings and the constants' own values are literal, and tests compare with the enums and constants (AGENT.md,
  Data and enums).
- **All the enums of a module are in ONE `enums.py` at the root of its `models` module** (`src/<module>/models/enums.py`,
  holding only enums, the one exception to one class per file), and **no enum value contains a hyphen**: values are
  lower snake case, `"not_started"` (AGENT.md, Data and enums).
- **EVERY logical branch logs** (`if`, `elif`, `else`, each `case`, each `except`), in `src/` outside `models/`: an early
  return, a skip or a default at `DEBUG`, a raise at `ERROR` first. A conditional expression that chooses what the code
  does becomes an `if`/`else`. Only the constructor's `logger if logger else getLogger(__name__)` and the code the
  logging system calls (formatters, handlers) stay silent (AGENT.md, Logging).


## The harness

This repository is a proof of concept for mastering the Claude Code harness; drone swarm piloting is the pretext (see
`README.md`). Its harness is versioned with the code, in `.claude/`.

- **Specifications:** `docs/specs/`, written with the `write-specs` skill under the SPEC rules
  (`.claude/rules/specs.md`, loaded by the `specs-rules` skill). Glossary first, then business rules, use cases, and
  features; every use case has an in-page Mermaid flow chart and a screen in light and dark mode for every state.
- **Generated content** (summaries, navigation, page list, matrix, back links, flow chart colours,
  `visual-identity.css`, the PNG screens) is written by `python3 .claude/skills/write-specs/scripts/specs.py build` and
  `render`, never by hand.
- **Done means checked:** `python3 .claude/skills/write-specs/scripts/specs.py check` prints nothing before any work on
  the specifications is reported as done.
- **Research and decisions:** `docs/research/landscape.md` (what exists) and `docs/research/interview.md` (what the
  product owner decided). A specification never states a fact that is not in one of them or given by the product owner.
- **Tickets:** the tickets of the roadmap (`docs/specs/roadmap/`) are worked by an agent graph, under the TKT rules
  (`.claude/rules/tickets.md`). `/ticket-plan <ID>` writes `docs/tickets/<ID>/TICKET.md` and a task graph in
  `PLAN.md`, then stops; the person approves the plan (`**Plan:** 🟢 Approved`); `/ticket-run <ID>` runs the waves in
  parallel worktrees, integrates, verifies, reviews, writes `EXPLAIN.md` and `IMPLEMENTATION.md` (TKT-14), then commits
  once and merges into `develop` locally.
- **Agents:** `.claude/agents/` (planner and reviewer on opus, workers on sonnet, mechanical work on haiku, TKT-7);
  workflows in `.claude/workflows/`.
- **Progress every 2 minutes** (TKT-9): when a ticket workflow starts, arm the Monitor tool with
  `python3 .claude/scripts/progress.py watch --every 120 --run <run id>` and relay each exhaustive report to the
  person in full, with its colour icons (phases, every agent with model, duration, tokens and result, tokens by model).
- **Commits:** no intermediate commit (TKT-5). A ticket's work stays uncommitted on `ticket/<ID>` while it runs, carried
  between worktrees by `.claude/scripts/ticket_tree.py`, and is committed once, when the ticket is done, then merged
  into `develop` locally. Nothing is ever pushed, and no commit is made outside the harness unless the person asks.
