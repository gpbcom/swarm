---
name: specs-rules
description: The enforced specification rules SPEC-1…SPEC-n for docs/specs/ (fixed layout and IDs, the glossary as the only source of persona/entity/system/term/state names, every feature referring to business rules and use cases, an in-page Mermaid flow chart of persona/entity interaction in every use case, a PNG screen for every state, one visual identity as design tokens, fixed sections, summaries, pagination, colours and icons, clickable links, generated content), read live from .claude/rules/specs.md. Load before writing, changing or reviewing any page, screen or mock-up under docs/specs/, together with the write-specs skill.
---

# Specification rules (SPEC)

**Source of truth:** `.claude/rules/specs.md`, loaded below as it is now. If the section below is empty or shows a
command instead of the rules, Read that file before going on. The file wins over anything else: never copy its rules
into another file.

## How to apply

1. Writing pages (procedure, templates, the `specs.py` script) is the **write-specs** skill. This skill holds the rules
   those pages must meet.
2. `python3 .claude/skills/write-specs/scripts/specs.py build`, then `... check`, which must print nothing.
3. A new specification rule the maintainer states goes into `.claude/rules/specs.md`, in its format, with the next free
   ID. If the script can check it, add the check to `specs.py` in the same change.

## Rules in force

!`cat "${CLAUDE_PROJECT_DIR:-.}/.claude/rules/specs.md"`
