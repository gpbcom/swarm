<!-- Review note template (TKT-6). Written by the reviewer for the person. -->
<!-- Keep it short: enough for the person to review the ticket in under an hour. Never restate the diff. -->

# {{ID}}: Review note

**Verdict:** {{✅ Approved or ⚠️ Changes requested}} · **Branch:** `ticket/{{ID}}`

## What changed

<!-- At most five bullets, each one behaviour or decision, not a file list. -->

- {{What changed, in one line}}.

## Acceptance criteria

<!-- One row per criterion of TICKET.md, in the same order. Evidence is a file of tests-evidences/ or a test name. -->

| Criterion | Evidence | Result |
| --- | --- | --- |
| {{1. Given ..., when ..., then ...}} | {{tests-evidences/...}} | {{✅ Pass or ❌ Fail}} |

## Look at first

<!-- The design and behaviour points the person should read, each with its files. -->
<!-- For identity, Operator isolation and Simulator isolation, name the files and read them line by line. -->

- {{Point to read}}: {{files}}.

## Assumptions accepted

<!-- Each assumption of TICKET.md and of the workers, with the reviewer's verdict on it (TKT-8). -->

- {{Assumption}}: {{accepted or rejected, and why}}.

## Follow-ups

<!-- Non-blocking findings (TKT-12). They never hold the merge. -->

- {{Follow-up}}.
