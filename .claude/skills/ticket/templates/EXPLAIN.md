<!-- Explanation template (TKT-14). Written by the explainer when the ticket is done, before its single commit. -->
<!-- For a developer who did not follow the ticket: how the delivered work works, and where it is, file by file and -->
<!-- line by line. Every claim points at a file and its lines. Never invent a behaviour the diff does not show. -->

# {{ID}}: {{Title}}

**Status:** ✅ Done · **Ticket:** [TICKET.md](TICKET.md) · **Choices and trade-offs:** [IMPLEMENTATION.md](IMPLEMENTATION.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🔭 What it does

<!-- Two to five bullets: what the ticket delivers, seen from outside (a user, a caller, a developer of the next -->
<!-- ticket). No file names here. -->

- {{What it does, in one line}}.

## ⚙️ How it works

<!-- The mechanism, in the order things happen at run time (or at build time for tooling): one numbered step per -->
<!-- moving part, each with a link to the file and the first line of the code that does it. -->
<!-- Link format: [`path/to/file.py:42`](../../../path/to/file.py#L42). -->

1. **{{Step}}:** {{what happens and why}}, in [`{{path}}:{{line}}`](../../../{{path}}#L{{line}}).

<!-- Add a Mermaid flowchart or sequenceDiagram when more than three parts talk to each other. -->

## 🧱 Files and lines changed

<!-- The table between the markers is generated: python3 .claude/scripts/ticket_tree.py changes --ticket {{ID}} --write -->
<!-- Never edit it by hand. Lines are those of the new version of each file. The ticket's own folder is left out. -->

<!-- changes -->
<!-- /changes -->

<!-- Then one bullet per file or group of files, in the order of the table: what changed in it and why, with the -->
<!-- line ranges that matter. -->

- [`{{path}}`](../../../{{path}}), lines {{a-b}}: {{what changed and why}}.

## 🧪 How to test it

<!-- The exact commands, from the repository root, and what each one shows. -->

```bash
{{command}}
```

## 🔗 Evidence

<!-- Links to tests-evidences/, with the result of each check. -->

- [{{Check}}](tests-evidences/{{file}}.txt): {{result}}.

## 📝 Assumptions accepted

<!-- The assumptions the reviewer accepted (TKT-8), one line each. Write "None." when there are none. -->

- {{Assumption}}.

## 🔜 Follow-ups

<!-- The non-blocking review findings (TKT-12), one row each. Write "None." when there are none. -->

| File | What to change |
| --- | --- |
| {{file}} | {{change}} |
