# 🎬 %ID%: %TITLE%

<!-- spec:nav-top -->
<!-- /spec:nav-top -->

**Status:** 🟡 Draft · **Updated:** %DATE%

> [!NOTE]
> {{One sentence: which persona does what, with which entity, and what they get.}}

<!-- spec:summary -->
<!-- /spec:summary -->

## <a id="actors"></a>👤 Personas and entities

| Name | Kind | Role in this use case |
| --- | --- | --- |
| [👤 {{Persona}}](../../glossary.md#per-{{persona}}) | Persona | {{What they do}} |
| [🗃️ {{Entity}}](../../glossary.md#ent-{{entity}}) | Entity | {{What happens to it}} |

## <a id="preconditions"></a>🚦 Preconditions

1. {{What is true before the use case starts.}}

## <a id="trigger"></a>⚡ Trigger

{{The event or the action that starts the use case.}}

## <a id="main-flow"></a>➡️ Main flow

1. The [👤 {{Persona}}](../../glossary.md#per-{{persona}}) {{does something}}.
2. {{Swarm does something with the entity}}.
3. {{...}}

## <a id="flowchart"></a>🔀 Flow chart

```mermaid
flowchart LR
    P1(["👤 {{Persona}}"]):::persona
    E1[("🗃️ {{Entity}}")]:::entity
    A1["{{Action}}"]:::action
    D1{"❓ {{Check}}"}:::decision
    OK(["✅ {{Outcome}}"]):::success
    KO(["❌ {{Error}}"]):::failure

    P1 -- "{{verb}}" --> A1
    A1 -- "{{reads or writes}}" --> E1
    A1 --> D1
    D1 -- "yes" --> OK
    D1 -- "no" --> KO

    classDef persona fill:#dbeafe,stroke:#1d4ed8,stroke-width:2px,color:#0b1f4d
    classDef entity fill:#dcfce7,stroke:#15803d,stroke-width:2px,color:#052e16
    classDef system fill:#ede9fe,stroke:#6d28d9,stroke-width:2px,color:#2e1065
    classDef action fill:#f1f5f9,stroke:#475569,color:#0f172a
    classDef decision fill:#fef3c7,stroke:#b45309,color:#451a03
    classDef success fill:#d1fae5,stroke:#047857,color:#022c22
    classDef failure fill:#fee2e2,stroke:#b91c1c,color:#450a0a
```

## <a id="screens"></a>🖼️ Screens

One row per state of the flow chart: every action, success and failure node. Each state shows its light then its dark screen; click one to open it full size. A state with nothing to show reads `➖ No screen: <why>`.

| State | Persona | Entity | Source | Screen |
| --- | --- | --- | --- | --- |
| <a id="screen-a1"></a>A1: {{Action}} | [🔄 {{Persona}}: {{State}}](../../glossary.md#st-{{persona}}-{{state}}) | [🔄 {{Entity}}: {{State}}](../../glossary.md#st-{{entity}}-{{state}}) | ✏️ Mock-up | [![%ID% A1: {{Action}}](../../screens/%ID%/a1.png)](../../screens/%ID%/a1.png) [![%ID% A1: {{Action}} (dark)](../../screens/%ID%/a1.dark.png)](../../screens/%ID%/a1.dark.png) |
| <a id="screen-ok"></a>OK: {{Outcome}} | [🔄 {{Persona}}: {{State}}](../../glossary.md#st-{{persona}}-{{state}}) | [🔄 {{Entity}}: {{State}}](../../glossary.md#st-{{entity}}-{{state}}) | ✏️ Mock-up | [![%ID% OK: {{Outcome}}](../../screens/%ID%/ok.png)](../../screens/%ID%/ok.png) [![%ID% OK: {{Outcome}} (dark)](../../screens/%ID%/ok.dark.png)](../../screens/%ID%/ok.dark.png) |
| <a id="screen-ko"></a>KO: {{Error}} | [🔄 {{Persona}}: {{State}}](../../glossary.md#st-{{persona}}-{{state}}) | [🔄 {{Entity}}: {{State}}](../../glossary.md#st-{{entity}}-{{state}}) | ✏️ Mock-up | [![%ID% KO: {{Error}}](../../screens/%ID%/ko.png)](../../screens/%ID%/ko.png) [![%ID% KO: {{Error}} (dark)](../../screens/%ID%/ko.dark.png)](../../screens/%ID%/ko.dark.png) |

## <a id="alternative-flows"></a>↪️ Alternative and error flows

| # | At step | Condition | What happens |
| --- | --- | --- | --- |
| A1 | {{2}} | {{When ...}} | {{...}} |

## <a id="business-rules"></a>📏 Business rules applied

| Rule | Where it applies |
| --- | --- |
| [📏 BR-{{NNN}}: {{Title}}](../business-rules/BR-{{NNN}}-{{slug}}.md) | {{Step 2}} |

## <a id="postconditions"></a>🏁 Postconditions

- ✅ **Success:** {{What is true at the end.}}
- ❌ **Failure:** {{What is true when it fails, and what the persona sees.}}

## <a id="referenced-by"></a>🔗 Referenced by

<!-- spec:referenced-by -->
<!-- /spec:referenced-by -->

<!-- spec:nav-bottom -->
<!-- /spec:nav-bottom -->
