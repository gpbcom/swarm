# 🛸 Swarm

**A proof of concept for mastering the Claude Code harness.** The product, an application that pilots a swarm of
drones, is the pretext: a domain rich enough (personas, missions, drones, safety rules, many states) to exercise what a
harness has to hold together.

> [!NOTE]
> The goal is not the drone software itself. It is to learn how far rules, skills, scripts and checks versioned with
> the code can make Claude Code produce consistent work, from specifications to code, with little supervision.

## 🎯 Why a harness

Claude Code reads the files of the repository it works in. A **harness** is the part of the repository written for it:
instructions, rules, skills, scripts and settings, versioned with the code. This PoC explores how to:

- write rules that are **checked by a script**, not only read, so that a breach is caught every time;
- package know-how as **skills** that load the right rules and templates for a task;
- keep generated content (summaries, navigation, diagrams, screens) **built by tools**, never by hand;
- make the result readable by people: colourised, illustrated, paginated, with clickable links.

## 🛸 The pretext: drone swarm piloting

Swarm is imagined as an application in which a pilot plans missions and flies several drones as one swarm. The
functional specification is the first deliverable, and the playground for the harness.

The dependencies in [services/gateway/pyproject.toml](services/gateway/pyproject.toml) sketch the direction: an API
(FastAPI), and agents (LangChain, LangGraph); the technical specification settles the rest. The root
[pyproject.toml](pyproject.toml) is the uv workspace that holds them together, with one `uv.lock` for the repository.
No product code is written yet.

The functional specification came out of an interview with the product owner, after a survey of what exists:

| Document | Holds |
| --- | --- |
| [🔭 Landscape](docs/research/landscape.md) | Commercial drone makers, multi-drone software, open autopilots, EU and US rules, and where blockchain helps (evidence, not flight) |
| [🎤 Interview](docs/research/interview.md) | The 72 decisions the specification rests on, from the interview rounds and final confirmations |
| [🏠 Specifications](docs/specs/README.md) | 22 features, 30 use cases, 27 business rules, the glossary and the visual identity, all approved |
| [🛠️ Technical interview](docs/research/interview-technical.md) | The 44 technical decisions: edge and cells, Python and Rust, NATS, PostgreSQL and TimescaleDB, Kubernetes with KEDA, React and Tauri |
| [🛠️ Technical specifications](docs/specs/technical/README.md) | Architecture, data models, storage, engine, API, security, scalability, observability, deployment, GUI and WebUI |

In short, Swarm is a suite (Mission studio, Ground control, Back office, Client portal, Simulator) that flies mixed
**Squads** (each Drone with its own model, payload and role) for four activities: light shows, agriculture, patrol and
inspection. It is hardware-agnostic (MAVLink, DJI, Skydio, Parrot), follows EU and US rules, keeps the Pilot in
command, uses AI agents that propose but never decide, and can anchor its evidence on a timestamping authority or a
blockchain.

## 🧭 What is in the repository

| Path | Holds |
| --- | --- |
| [CLAUDE.md](CLAUDE.md) | The entry point Claude Code reads first: how the harness is organised |
| [AGENT.md](AGENT.md) | How code is written: layout, typing, logging, tests |
| [.claude/rules/specs.md](.claude/rules/specs.md) | The specification rules SPEC-1 to SPEC-13 |
| [.claude/skills/specs-rules/](.claude/skills/specs-rules/SKILL.md) | The skill that loads those rules |
| [.claude/skills/write-specs/](.claude/skills/write-specs/SKILL.md) | The skill that writes specifications: procedure, templates and the `specs.py` script |
| [docs/specs/](docs/specs/README.md) | The specifications themselves |
| [services/](services/) | The backend services, one folder each. The gateway service ([services/gateway/](services/gateway/)) moved here from the root `src/` |
| [packages/](packages/) | The code several services share: `python/` (uv), `rust/` (Cargo, with maturin) and `ts/` (pnpm) |
| [frontends/](frontends/) | The front ends, one folder each, not started yet |
| [deploy/terraform/](deploy/terraform/README.md) | Terraform: one module per building block, and the root of the dev cell |
| [tests/](tests/) | The convention tests, which run against every service |

## 📚 The specifications

The [specifications](docs/specs/README.md) follow rules that a script checks:

- a [📖 glossary](docs/specs/glossary.md) is the only source of names for personas, entities, systems, terms and
  states, and refuses their synonyms;
- every 📘 feature refers to 📏 business rules and 🎬 use cases;
- every use case has a Mermaid flow chart of the interaction between its personas and entities, and a PNG screen for
  every state of that chart, in light and dark mode;
- a [🎨 visual identity](docs/specs/visual-identity.md), written as design tokens with a light and a dark value, gives
  screens and diagrams the same colours, fonts and sizes;
- every page has a summary, a page number, previous and next links, icons and colour.

To work on them, ask Claude Code to write or change a specification: the `write-specs` skill takes over. By hand:

```bash
python3 .claude/skills/write-specs/scripts/specs.py new uc "Launch a mission"   # create a use case
python3 .claude/skills/write-specs/scripts/specs.py render                      # render the mock-up screens to PNG
python3 .claude/skills/write-specs/scripts/specs.py check                       # prints nothing when all is well
```

Rendering screens needs Chrome or Chromium (or `SPECS_BROWSER` set to one).

## 🚀 How to start

### Prerequisites

- [uv](https://docs.astral.sh/uv/), which installs Python 3.12 for the project.
- A stable Rust toolchain. [packages/rust/rust-toolchain.toml](packages/rust/rust-toolchain.toml) selects it.
- Node LTS, with [corepack](https://nodejs.org/api/corepack.html) to provide pnpm.
- [Terraform](https://developer.hashicorp.com/terraform) 1.10 or later, only for
  [deploy/terraform](deploy/terraform/README.md).

### Install the workspaces

From a clean clone, run these commands in order:

```bash
uv sync
cargo fetch --manifest-path packages/rust/Cargo.toml
corepack enable && pnpm install
```

Each command installs one workspace: uv for Python (one `uv.lock`), Cargo for Rust, and pnpm for TypeScript.

### Run the checks

```bash
uv run ruff check services packages tests
uv run mypy services/gateway/src
uv run pytest services/gateway/tests -n 2
uv run pytest tests/conventions
pnpm turbo run build
```

### Provision the dev cell

Terraform creates the dev cell's machines, network and k3s cluster. Follow
[deploy/terraform/README.md](deploy/terraform/README.md).
