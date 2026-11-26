---
name: write-specs
description: Create and update the functional and technical specifications under docs/specs/: glossary (personas, entities, systems, terms, states), visual identity (design tokens, components, screen size), features (FS), use cases (UC) with their in-page Mermaid flow charts and a PNG screen for every state, business rules (BR), the index and the traceability matrix, paginated, colourised, with icons and clickable links, generated, rendered and checked by specs.py. Use when asked to write, add, change, review or reorganise a specification, a feature, a use case, a business rule, a persona, a state, a glossary entry, a screen, a mock-up or the visual identity, or to describe what Swarm should do.
---

# Write the specifications

The rules are **SPEC-1…SPEC-n** in `.claude/rules/specs.md`. Load the **specs-rules** skill first: this skill says how
to work, the rules say what the result must be.

The script is `.claude/skills/write-specs/scripts/specs.py` (Python with Pillow, plus Chrome or Chromium for
rendering). `render` saves every screen as a 256-colour palette PNG; a screenshot of the application must be
converted the same way before `check` accepts it. Below, `specs.py` means:

```bash
python3 .claude/skills/write-specs/scripts/specs.py <command>
```

| Command | Does |
| --- | --- |
| `init` | Creates the fixed pages, `components.css` and the component sheet when missing or empty, then renders |
| `new fs\|uc\|br "Title"` | Creates the next feature, use case or business rule from its template, then builds |
| `mockup <UC-ID> <node>` | Creates the HTML mock-up of one state (a flow chart node) of a use case |
| `render [--all] [<UC-ID>...]` | Builds, then renders every mock-up whose PNG is missing or out of date |
| `build` | Rewrites the generated content: page list, summaries, navigation, matrix, back links, palette, flow chart colours, `visual-identity.css`, `frontend/packages/tokens/src/tokens.css` |
| `check` | Prints one line per breach, `<file>: SPEC-<n>: <message>`, and nothing when all is well |

The templates are in `templates/`. Never copy one by hand: `new` and `mockup` name the files.
If no browser is found, set `SPECS_BROWSER` to the path of Chrome or Chromium.

## Procedure

1. **Understand before writing.** Read `docs/specs/README.md`, the glossary, the visual identity and the pages the
   request touches. If `docs/specs/README.md` is empty or missing, run `specs.py init`.
2. **Ask for what is missing.** A specification states facts the maintainer gives. When a persona, a limit, a rule, a
   state or an outcome is unknown, ask the maintainer (AskUserQuestion) or write it under **❓ Open questions** of the
   feature. Never invent it (SPEC-10).
3. **Glossary first** (SPEC-2). Add every new persona, entity, system, term and **state** to
   `docs/specs/glossary.md` before any other page uses it, with its definition and its **Do not say** synonyms. A
   state reads `<Persona or entity>: <State>`, such as `Drone: Airborne`. Reuse existing names.
4. **Business rules next.** `specs.py new br "Title"` for each rule. One rule per page, one sentence with MUST, MUST
   NOT or MAY, and at least one ✅ allowed and one ❌ refused example.
5. **Use cases.** `specs.py new uc "Title"` for each interaction.
   1. List its personas, entities and systems in **👤 Personas and entities**, each linked to the glossary.
   2. Write the main flow and the alternative flows.
   3. Draw the flow chart **in the page**, in a ` ```mermaid ` block (SPEC-4): every persona, entity and system of
      the list is a node, every step and error is a node, the arrows carry the verbs. Leave the `classDef` lines as
      the template has them: `build` sets their colours.
   4. Fill **🖼️ Screens** (SPEC-12): one row per action, success and failure node, naming the persona and entity
      **states** of the glossary in that node.
   5. For each row: `specs.py mockup <UC-ID> <node>`, then draw the screen in the HTML file with the classes of
      `components.css` only (see the component sheet in the visual identity). Use glossary names on screen and the
      same fictional sample data across the use case. A state that shows nothing gets `➖ No screen: <why>`.
   6. `specs.py render <UC-ID>`, then **open every PNG** (Read tool) and check it shows the state as described.
6. **The feature last.** `specs.py new fs "Title"`. Link its business rules and its use cases (SPEC-3), and write one
   acceptance criterion per behaviour, each naming its rule and use case.
7. **Build, then check.** `specs.py build`, then `specs.py check`. Fix every line it prints and run both again until
   `check` prints nothing. Never edit generated content (SPEC-11).
8. **Read it back.** Open the changed pages and check by reading what the script cannot: the flow chart matches the
   steps, every glossary state is really what the screen shows, functional pages say nothing about how the product is
   built.
9. **Report** the pages and screens created or changed, each as a clickable link, and the open questions left.

## Visual identity

- `docs/specs/visual-identity.md` is the only place where a colour, a font, a size or the screen size is chosen
  (SPEC-13). Its tokens become `screens/mockups/visual-identity.css`, `frontend/packages/tokens/src/tokens.css` and the flow chart colours on `build`.
- New component: add its class to `screens/mockups/components.css` (with `var(--...)` only), add it to the
  **🧩 Components** table and to `screens/mockups/identity/components.html`, then `specs.py render --all`.
- Changing a token or a component makes every PNG out of date: run `specs.py render --all`, then look at the
  component sheet and at a few screens before reporting.
- A change of look the maintainer has not asked for is proposed, not made.

## Changing existing pages

- **Renaming a glossary entry:** change its row, add the old name to its **Do not say** column, then run `check`: it
  lists every page and mock-up that still uses the old name.
- **The application now shows a state:** capture the real window at the screen size of the visual identity, save it
  over `screens/<UC-ID>/<node>.png`, set the row's source to `📸 Screenshot`, and delete the mock-up.
- **Retiring a page:** set its status to 🔴 Deprecated and say why in its summary note. Do not delete it and do not
  reuse its ID (SPEC-1).
- **Splitting a page:** create the new pages with `new`, move the content and the screens, and update every link.
- **Review:** after changes by someone else, run `check` first, then read for the rules it cannot check.

## Writing well

- Each page answers one question. Its `> [!NOTE]` line under the title says what it is in one sentence.
- Name the persona in every step of a main flow: "The [👤 Pilot](../../glossary.md#per-pilot) plans a
  [🗃️ Mission](../../glossary.md#ent-mission)", not "a mission is planned".
- Link the first mention of each persona, entity and system on a page, then write the name plainly.
- Prefer tables to long paragraphs, and short sentences to long ones. British English, no em dash.
