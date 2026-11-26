# Specification rules

These rules apply to every page under `docs/specs/`, functional and technical. They apply to anyone who writes a
specification, people and AI agents alike. The `write-specs` skill applies them, and its script checks them.

## How this file works

- Each rule has an ID (`SPEC-<n>`) that never changes. Reviews and discussions can cite it ("breaks SPEC-4").
- New rules are added at the end with the next free ID and a row in the summary table. A rule that is dropped stays in
  the file, marked **Withdrawn** with the date, so that its ID is never reused.
- Each rule has the same parts: **Rule**, **Why**, **Check**.
- Every check is run by one command, which must print nothing:

  ```bash
  python3 .claude/skills/write-specs/scripts/specs.py build
  python3 .claude/skills/write-specs/scripts/specs.py check
  ```

| ID | Rule | Enforced since |
| --- | --- | --- |
| [SPEC-1](#spec-1) | The specifications follow one layout, and each feature, use case and business rule has a fixed ID | 2026-11-18 |
| [SPEC-2](#spec-2) | The glossary is the only source of names for personas, entities, systems, terms and states | 2026-11-18 |
| [SPEC-3](#spec-3) | Every feature refers to at least one business rule and one use case, and nothing is orphaned | 2026-11-18 |
| [SPEC-4](#spec-4) | Every use case has, in its page, a Mermaid flow chart of the interaction between its personas and its entities | 2026-11-18 |
| [SPEC-5](#spec-5) | Every page has the sections of its kind, in order, each with an anchor | 2026-11-18 |
| [SPEC-6](#spec-6) | There is a summary of all pages, and a summary at the top of each page | 2026-11-18 |
| [SPEC-7](#spec-7) | The specifications are paginated, with navigation at the top and the bottom of each page | 2026-11-18 |
| [SPEC-8](#spec-8) | Pages are colourised and use the icons of this file, and no others for the same meaning | 2026-11-18 |
| [SPEC-9](#spec-9) | Every reference is a clickable link, and every link works | 2026-11-18 |
| [SPEC-10](#spec-10) | Pages are written in plain British English, with no placeholder and no invented fact | 2026-11-18 |
| [SPEC-11](#spec-11) | Generated content is written by the script only | 2026-11-18 |
| [SPEC-12](#spec-12) | Every state of every use case has its PNG screen, in light and dark mode, or says why it has none | 2026-11-18 |
| [SPEC-13](#spec-13) | The visual identity is specified once, as tokens with a light and a dark value, and every screen and diagram uses it | 2026-11-18 |

## <a id="spec-1"></a>SPEC-1: One layout, fixed IDs

**Rule:**

| Path | Holds | Title |
| --- | --- | --- |
| `docs/specs/README.md` | The index: the list of all pages and the legend | `# 🏠 Swarm specifications` |
| `docs/specs/glossary.md` | The glossary | `# 📖 Glossary` |
| `docs/specs/visual-identity.md` | The visual identity: tokens, components, screen rules (SPEC-13) | `# 🎨 Visual identity` |
| `docs/specs/functional/README.md` | The functional overview and the traceability matrix | `# 🧭 Functional specifications` |
| `docs/specs/functional/features/FS-<nnn>-<slug>.md` | One feature (functional specification) | `# 📘 FS-<nnn>: <Title>` |
| `docs/specs/functional/use-cases/UC-<nnn>-<slug>.md` | One use case | `# 🎬 UC-<nnn>: <Title>` |
| `docs/specs/functional/business-rules/BR-<nnn>-<slug>.md` | One business rule | `# 📏 BR-<nnn>: <Title>` |
| `docs/specs/technical/README.md` | The technical overview | `# 🛠️ Technical specifications` |
| `docs/specs/technical/**/*.md` | Technical pages | `# <icon> <Title>` |
| `docs/specs/roadmap/README.md` | The roadmap overview | `# 🛣️ Roadmap` |
| `docs/specs/roadmap/**/*.md` | Roadmap pages | `# <icon> <Title>` |

- `docs/specs/screens/` holds the screens (SPEC-12): `<UC-ID>/<node>.png`, the mock-ups in
  `mockups/<UC-ID>/<node>.html`, `mockups/components.css` and the generated `mockups/visual-identity.css`. The
  `identity/` group holds the component sheet of the visual identity.
- No other Markdown file sits under `docs/specs/`.
- `<nnn>` is three digits. An ID is never reused, even when its page is deleted: a page that no longer applies is
  marked 🔴 Deprecated instead.
- `<slug>` is the title in kebab case. Create pages with `specs.py new fs|uc|br "Title"`, which picks the next ID.
- A page has exactly one `#` title.

**Why:** a reader, a reviewer or an agent finds any page from its ID alone, and an ID cited somewhere keeps pointing
at the same thing.

**Check:** `specs.py check` reports pages outside the layout, missing fixed pages, bad file names, duplicate IDs and
titles that do not match the ID.

## <a id="spec-2"></a>SPEC-2: The glossary is the only source of names

**Rule:**

- Every persona, entity, system and term used in the specifications has one row in `docs/specs/glossary.md`, in its
  section, in this format:

  ```markdown
  | <a id="per-operator"></a>👤 **Operator** | The person who ... | user, admin |
  ```

  | Section | Anchor prefix | Icon | For |
  | --- | --- | --- | --- |
  | 👤 Personas | `per-` | 👤 | The people, or roles, who interact with the product |
  | 🗃️ Entities | `ent-` | 🗃️ | The things the product stores, receives or produces |
  | ⚙️ Systems | `sys-` | ⚙️ | The product itself and the external systems it talks to |
  | 🔤 Terms | `term-` | 🔤 | Other words with a precise meaning |
  | 🔄 States | `st-` | 🔄 | A state a persona or an entity can be in, named `<Persona or entity>: <State>`, such as `Drone: Grounded` |

- The third column, **Do not say**, lists the synonyms readers might use. They never appear in a specification page,
  in prose or in a flow chart: the glossary name is written instead.
- A name is written exactly as in the glossary, in prose, in tables and in flow charts. A plural adds `s` or `es`.
- The first time a page mentions a persona, entity or system, it links to its glossary row:
  `[👤 Operator](../../glossary.md#per-operator)`. The link text is the glossary name.
- A new name is added to the glossary **before** it is used on another page.
- On-screen text of the mock-ups uses the same names: the **Do not say** words are refused there too.

**Why:** two names for one thing, or one name for two things, is the most common source of wrong implementations.
Personas in particular must read the same in the features, the use cases and the flow charts.

**Check:** `specs.py check` reports malformed or duplicate glossary rows, any **Do not say** word found on a page, a
glossary link whose text is not the name of its row, a flow chart persona, entity or system that is not in the
glossary under that kind, and a state whose owner is not a persona or an entity of the glossary.

## <a id="spec-3"></a>SPEC-3: Features refer to business rules and use cases

**Rule:**

- Every feature (📘 FS) links, in its section **📏 Business rules**, to at least one business rule (📏 BR), and in its
  section **🎬 Use cases**, to at least one use case (🎬 UC).
- Every acceptance criterion of a feature names the business rule and the use case it verifies.
- Every use case and every business rule is referred to by at least one feature. A use case lists, in its section
  **📏 Business rules applied**, the rules it applies.
- A link to a feature, use case or business rule shows its ID in its text: `[📏 BR-001: Title](...)`.
- The traceability matrix in `functional/README.md` and the **🔗 Referenced by** section of each use case and business
  rule are generated from these links (SPEC-11).

**Why:** a feature without a rule cannot be verified, and a rule or a use case no feature needs is either missing a
feature or should not exist.

**Check:** `specs.py check` reports a feature without a business rule or a use case, an orphan use case or business
rule, and a link to one of them without its ID.

## <a id="spec-4"></a>SPEC-4: Every use case has a flow chart

**Rule:** the section **🔀 Flow chart** of every use case holds a Mermaid `flowchart`, written in a ` ```mermaid `
block of the page itself (never an image, never a link to another file), that shows the interaction between the
personas and the entities of the use case.

- The personas, entities and systems of the chart are exactly those of the section **👤 Personas and entities**: each
  one listed there is in the chart, and each one in the chart is listed there with a link to its glossary row.

- It has at least one persona node and one entity node. Every persona, entity and system node takes part in at least
  one arrow, and arrows carry the verb of the interaction: `P1 -- "submits" --> A1`.
- Node labels are quoted, start with their icon, and use these shapes and classes:

  | Node | Syntax |
  | --- | --- |
  | 👤 Persona | `P1(["👤 Operator"]):::persona` |
  | 🗃️ Entity | `E1[("🗃️ Task")]:::entity` |
  | ⚙️ System | `S1[["⚙️ Swarm"]]:::system` |
  | Action | `A1["Validate the task"]:::action` |
  | ❓ Decision | `D1{"❓ Is it valid?"}:::decision` |
  | ✅ Success | `OK(["✅ Task queued"]):::success` |
  | ❌ Failure | `KO(["❌ Task refused"]):::failure` |

- The persona, entity and system labels are glossary names (SPEC-2).
- Every action, success and failure node is a **state** of the use case, and has its row in **🖼️ Screens**
  (SPEC-12).
- The flow chart matches the **➡️ Main flow** and the **↪️ Alternative and error flows**: every step and every error
  appears in it.

**Why:** the flow chart is the part a reader looks at first. It shows who does what to which entity, and where it can
fail, faster than the numbered steps.

**Check:** `specs.py check` reports a use case without a flow chart in its page, without a persona or an entity
node, a node in no arrow, a node name that is not in the glossary, a persona or entity listed in the use case but
missing from the chart, and the reverse. Whether the chart
matches the steps is checked by reading.

## <a id="spec-5"></a>SPEC-5: Fixed sections, in order

**Rule:** each page has the sections of its kind, in this order. Every `##` heading reads
`## <a id="<anchor>"></a><icon> <Title>`. Other sections may be added between them.

| Kind | Sections (anchor) |
| --- | --- |
| 🏠 Index | `pages`, `legend` |
| 📖 Glossary | `personas`, `entities`, `systems`, `terms`, `states` |
| 🎨 Visual identity | `principles`, `colours`, `typography`, `spacing`, `iconography`, `components`, `screens`, `diagrams` |
| 🧭 Functional overview | `overview`, `traceability` |
| 📘 Feature | `goal`, `personas`, `business-rules`, `use-cases`, `acceptance`, `out-of-scope`, `open-questions`, `references` |
| 🎬 Use case | `actors`, `preconditions`, `trigger`, `main-flow`, `flowchart`, `screens`, `alternative-flows`, `business-rules`, `postconditions`, `referenced-by` |
| 📏 Business rule | `statement`, `rationale`, `examples`, `exceptions`, `referenced-by` |
| 🛠️ Technical overview | `overview` |
| 🛣️ Roadmap overview | `overview` |

- Features, use cases, business rules and the visual identity start with a status line: `**Status:** 🟡 Draft · **Updated:** <date>`.
- A business rule also has `**Type:**`, one of Constraint, Validation, Computation, Authorisation or Inference. Its
  statement is one sentence using MUST, MUST NOT or MAY, and its examples include at least one ✅ allowed and one ❌
  refused case.
- Acceptance criteria are written **Given**, **when**, **then**.

**Why:** the same question always has its answer in the same place, so pages can be read, reviewed and compared
quickly.

**Check:** `specs.py check` reports a heading without an anchor, a missing section, sections out of order, a missing
or unknown status and a missing rule type.

## <a id="spec-6"></a>SPEC-6: Summaries

**Rule:**

- The index (`docs/specs/README.md`) holds the summary of the whole specification: the numbered list of every page,
  with its kind and its status, each a link.
- Every page holds its own **📑 Summary**, below its title and status, linking to each of its sections.
- Both are generated between `<!-- spec:pages -->` and `<!-- spec:summary -->` markers (SPEC-11).

**Why:** a reader sees what exists and jumps to it without scrolling.

**Check:** `specs.py check` reports a page without its summary markers and a summary that is out of date.

## <a id="spec-7"></a>SPEC-7: Pagination

**Rule:**

- The pages form one numbered sequence: index, glossary, visual identity, functional overview, features, use cases, business rules,
  technical overview, technical pages, roadmap overview, roadmap pages. Inside a kind, pages follow their ID or their path.
- Every page starts and ends with a navigation bar: 🏠 Index, ◀️ previous page, `📄 Page n / N`, next page ▶️.
- The bars are generated between the `<!-- spec:nav-top -->` and `<!-- spec:nav-bottom -->` markers (SPEC-11).
- One page holds one feature, one use case or one business rule. A page that grows past what a reader takes in at
  once is split into several pages, each with its own ID.

**Why:** the specification reads like a document, from the first page to the last, and each page stays short.

**Check:** `specs.py check` reports a page without its navigation markers and a navigation bar that is out of date.

## <a id="spec-8"></a>SPEC-8: Colours and icons

**Rule:**

- **Titles:** each kind of page has its icon (SPEC-1). Every `##` heading starts with an icon that says what the
  section holds.
- **Status:** 🟡 Draft, 🔵 In review, 🟢 Approved, 🔴 Deprecated. No other status.
- **Callouts:** GitHub alerts give colour to what matters: `> [!NOTE]` for the one-line summary of a page,
  `> [!IMPORTANT]` for the statement of a business rule, `> [!WARNING]` for exceptions and open questions,
  `> [!TIP]` for reading advice, `> [!CAUTION]` for anything destructive or irreversible.
- **Flow charts:** use only the classes of SPEC-4. Their colours come from the tokens of the visual identity
  (SPEC-13) and are listed, generated, in its section **🔀 Diagrams**. `specs.py build` writes them into every
  `classDef` line: never pick a colour by hand.

- **Icons:** one meaning, one icon, everywhere:

  | Icon | Meaning | Icon | Meaning |
  | --- | --- | --- | --- |
  | 🏠 | Index | 🎯 | Goal |
  | 📖 | Glossary | 🚦 | Preconditions |
  | 🧭 | Functional overview | ⚡ | Trigger |
  | 🛠️ | Technical | ➡️ | Main flow |
  | 📘 | Feature | 🔀 | Flow chart |
  | 🎬 | Use case | ↪️ | Alternative and error flows |
  | 📏 | Business rule | 🏁 | Postconditions |
  | 👤 | Persona | 📌 | Statement |
  | 🗃️ | Entity | 💡 | Rationale |
  | ⚙️ | System | 🧪 | Examples |
  | 🔤 | Term | ⚠️ | Exceptions |
  | 📑 | Summary | ✅ | Acceptance criteria, success |
  | 📄 | Page number | ❌ | Refused, failure |
  | ◀️ ▶️ | Previous, next page | 🚫 | Out of scope |
  | 🔗 | References, referenced by | ❓ | Open questions, decision |
  | 🧬 | Traceability | 🔭 | Overview |
  | 🎨 | Visual identity | 🖼️ | Screens |
  | 🔄 | State | ✏️ | Mock-up |
  | 📸 | Screenshot | ➖ | No screen, not applicable |
  | 💎 | Principles | 🌈 | Colours |
  | 🔠 | Typography | 📐 | Spacing and shapes |
  | 🔣 | Iconography | 🧩 | Components |
  | 🗺️ | Legend | 📚 | Pages |
  | ⏳ | In progress | ⚠️ | Warning |
  | 🛸 | Drone, on maps and in lists | ✋ | Hold |
  | 🛑 | Abort | 🎮 | Manual control, Control mapping |
  | 🗺️ | Map, list of Missions | 🛰️ | Flight view of Ground control |
  | 📋 | Pre-flight check | 🎥 | Live video |
  | 📼 | Replay, Debrief | 📊 | Plan against actual |
  | 🔬 | Quality checks | 🧾 | Scorecard |
  | 📈 | Progress | 📜 | Authorisations |
  | 📦 | Deliverables | 🔏 | Evidence record |
  | 👥 | People and access | 🔧 | Settings |
  | ➕ | Order, create | 🔔 | Alarm, notification |
  | 💬 | Conversation with an AI agent | 🖊️ | Design a Mission |
  | 🕹️ | Simulator | 📡 | Links |
  | 🗒️ | Details settled with the product owner | 🔍 | Focus view |
  | 🏗️ | Architecture | 🧱 | Data models |
  | 🗄️ | Storage | 🔩 | Engine and services |
  | 🔌 | API layer | 🔐 | Security |
  | 🚀 | Scalability and performance | 🩺 | Observability |
  | 🚢 | Deployment | 🖥️ | GUI and WebUI |
  | ⏱️ | Performance budget | ⚖️ | Decisions (technical) |
  | 🗂️ | Mono-repo, repository layout | 🌐 | Edge and core, network |
  | 🔲 | Cells | 🔁 | Data flows |
  | 🏷️ | Conventions | 📨 | Messages and events |
  | 🔢 | Versioning | 🧮 | Algorithms |
  | 🔑 | Identity and keys | 🛡️ | Protection, threats |
  | 🧰 | Toolchain | 📉 | Capacity and sizing |
  | 🕰️ | Time series | 🪣 | Object storage |
  | 🗑️ | Retention | 💾 | Backups and recovery |
  | 🧷 | Drone adapters | 🏭 | Processing |
  | 🏋️ | Load tests | 🏢 | On premises |
  | 🌱 | Environments | 🚢 | Delivery, deployment |
  | 🛣️ | Roadmap, phase | 📆 | Timeline |
  | 🏆 | Milestones | 🧺 | Scope |
  | 🪜 | Epics | 🗓️ | Sprint plan |
  | 🎤 | Demo | 🚪 | Exit criteria |
  | ⛓️ | Dependencies | 🎲 | Risks |
  | 🏛️ | Regulation | 🛫 | Flight tests |
  | 🤝 | Partners and hardware | 🧑‍💻 | Work split (person and agents) |
  | 🧅 | Layers inside a service | 🎫 | Tickets |

**Why:** colour and icons let a reader tell a persona from an entity, a rule from a use case, or a draft from an
approved page at a glance, and the same colour always means the same thing.

**Check:** `specs.py check` reports a title or a heading without its icon, an unknown status and a flow chart class
outside the visual identity or with another definition. The choice of icons for added sections is checked by reading.

## <a id="spec-9"></a>SPEC-9: Clickable links

**Rule:**

- Every mention of another page, of a glossary row or of a section is a relative Markdown link, never a bare name or
  path: `[🎬 UC-001: Submit a task](../use-cases/UC-001-submit-a-task.md)`.
- Links to a section point to an explicit anchor, `<a id="...">`, never to a heading slug, because slugs differ
  between GitHub, VS Code and other viewers.
- Every link resolves: the file exists and the anchor is in it. Anchors are unique on their page.

**Why:** a specification is read by jumping from a feature to its rules, from a use case to its personas, and back. A
broken or missing link breaks that path.

**Check:** `specs.py check` reports broken links, missing anchors and duplicate anchors.

## <a id="spec-10"></a>SPEC-10: Writing

**Rule:**

- Plain British English (`colour`, `behaviour`, `organisation`), short sentences, no em dash.
- No placeholder (`{{...}}`) is left on a page.
- Nothing is invented. A fact nobody has given (a limit, a price, a role, a delay) goes under **❓ Open questions** of
  the feature and is asked, not guessed.
- Functional pages say what the product does and why, never how it is built: no class, table, endpoint or library
  names. Those belong to the technical pages, which link to the features they implement.

**Why:** a guessed fact in a specification becomes a wrong requirement that looks agreed.

**Check:** `specs.py check` reports em dashes and placeholders. The rest is checked by reading.

## <a id="spec-11"></a>SPEC-11: Generated content

**Rule:**

- `specs.py build` writes, and nobody edits by hand:
  - the text between `<!-- spec:<name> -->` and `<!-- /spec:<name> -->`: page lists, summaries, navigation bars, the
    traceability matrix, **🔗 Referenced by** and the palette of the visual identity;
  - the style of every `classDef` line of the flow charts;
  - `docs/specs/screens/mockups/visual-identity.css`;
  - `frontend/packages/tokens/src/tokens.css`, the same tokens for the apps, beside it.
- `specs.py render` writes the PNG of every mock-up (SPEC-12).
- Run `specs.py build` after every change to `docs/specs/`, then `specs.py check`, which must print nothing before the
  work is reported as done.

**Why:** a summary, a page number or a matrix maintained by hand drifts at the first change.

**Check:** `specs.py check` reports every page, `visual-identity.css` and `frontend/packages/tokens/src/tokens.css`, that differs from what `build` would write.

## <a id="spec-12"></a>SPEC-12: A screen for every state

**Rule:**

- Every use case has a section **🖼️ Screens**, right after its flow chart, with one row per **state**: every
  action, success and failure node of the flow chart. Decision nodes may have a row too.
- A row reads:

  ```markdown
  | <a id="screen-a1"></a>A1: Plan the route | [👤 Mission planner](../../glossary.md#per-mission-planner) | [🔄 Mission: Draft](../../glossary.md#st-mission-draft) | ✏️ Mock-up | [![UC-001 A1: Plan the route](../../screens/UC-001/a1.png)](../../screens/UC-001/a1.png) [![UC-001 A1: Plan the route (dark)](../../screens/UC-001/a1.dark.png)](../../screens/UC-001/a1.dark.png) |
  ```

  | Cell | Holds |
  | --- | --- |
  | State | The anchor `screen-<node id in lower case>`, then the node ID and its label |
  | Persona | The persona of the chart in this state: a link to its 🔄 state row of the glossary, or to the persona, or `➖` |
  | Entity | The entity of the chart in this state: a link to its 🔄 state row, or to the entity, or `➖` |
  | Source | `✏️ Mock-up`, `📸 Screenshot`, or `➖` when nothing is shown |
  | Screen | The light PNG then the dark PNG, each clickable to open it full size, or `➖ No screen: <why nothing is shown>` |

- **Every state of the glossary** (🔄 States, SPEC-2) appears in at least one screen row of a use case.
- Every screen exists in **light and dark mode**: `docs/specs/screens/<UC-ID>/<node id in lower case>.png` and
  `<node id in lower case>.dark.png`, both exactly `screen.width` x `screen.height` of the visual identity, saved as
  256-colour palette PNGs (to keep the repository small), and shown on a page. Their image texts start with the use case ID.
- **✏️ Mock-up:** until the application shows the state. Its source is
  `docs/specs/screens/mockups/<UC-ID>/<node>.html`, created with `specs.py mockup <UC-ID> <node>`, drawn with the
  classes of `components.css` only, and rendered by `specs.py render` in both modes. Each PNG records a hash of its
  source and mode: when the mock-up, `components.css` or the visual identity changes, `check` asks for a new render.
- **📸 Screenshot:** once the application shows the state, captures of the real window in light and dark mode
  replace the mock-up, at the same paths, and the mock-up is deleted.
- `➖ No screen` is for a state that shows nothing to anyone (a background step), and says why.

**Why:** a state described only in words is read differently by each person. One picture per state shows what the
persona sees, settles the wording on screen, and becomes the reference the application is compared to.

**Check:** `specs.py check` reports a state of the chart without a row, a row matching no state, a persona or entity
cell that is not a glossary row of the chart's personas or entities, a glossary state no use case shows, a missing,
wrong-sized, unrendered or out-of-date PNG, a PNG without its other mode, a PNG shown on no page, and a mock-up
without its two PNGs.

## <a id="spec-13"></a>SPEC-13: One visual identity

**Rule:**

- `docs/specs/visual-identity.md` specifies the look of Swarm once, for the application, the screens of the use
  cases and the diagrams: principles, colours, typography, spacing, iconography, components, screen size and
  screenshot rules.
- Every value is a **token**, a table row `` | `<group>.<name>` | `<light value>` | `<dark value>` | ... | ``. Every
  colour has a light and a dark value, both lower-case `#rrggbb`; other tokens may leave the dark value empty when it
  is the same. Sizes, spaces, radii and the screen size are in `px`. The required tokens are listed in
  `spec_model.py` (`REQUIRED_TOKENS`).
- `specs.py build` writes the tokens as CSS variables into `screens/mockups/visual-identity.css` and into the tokens
  package `frontend/packages/tokens/src/tokens.css`, the dark values under `prefers-color-scheme: dark`, and the light colours
  into every flow chart (SPEC-8).
- The visual identity also fixes the **frame of each part of Swarm** (title bar, side bar items, status bar), so that
  every screen of Ground control, the Mission studio, the Back office and the Client portal looks the same.
- `screens/mockups/components.css` defines the components with `var(--...)` only: no colour and no font value of its
  own. Mock-ups link these two stylesheets and nothing else, and have no `style` attribute or `<style>` block.
- The visual identity has its component and layout sheets, `screens/identity/components.png` and `layouts.png`, in
  both modes, rendered from `screens/mockups/identity/`. Together they show every component.
- A change of look is a change of tokens or components, made on this page and in `components.css`, then built and
  rendered: never a one-off value in a screen.

**Why:** screens drawn by different people, or by an agent at different times, drift apart unless they share one
source. Tokens also let the application reuse the exact colours and sizes of the specification.

**Check:** `specs.py check` reports a missing or malformed token, a colour without its dark value, a stale
`visual-identity.css`, a raw colour or font in `components.css`, a mock-up with its own style or another stylesheet,
and a PNG of the wrong size, without its other mode, or not a 256-colour palette PNG.
