# T0.15: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- A message in English only must make CI fail, and the shells must switch language without reloading (acceptance criteria of [TICKET.md](TICKET.md), from [📏 BR-017](../../specs/functional/business-rules/BR-017-every-screen-in-four-languages.md)).
- A person's language is stored with the person and applied at sign-in ([📘 FS-012](../../specs/functional/features/FS-012-operators-deployment-and-languages.md), AC-2).
- Python messages are Babel catalogues in `packages/python`, translated into the person's language ([🔩 Engine and services](../../specs/technical/04-engine.md)).
- One class per file, all enums in one `models/enums.py`, no raw string in `src/`, and every branch logs ([`AGENT.md`](../../../AGENT.md), File shape, Data and enums, Logging).
- A model shared between services lives in `swarm-models` and its schema, Rust and TypeScript types are generated ([`AGENT.md`](../../../AGENT.md), Shared models).
- The area of the ticket is `packages/ts/i18n`, `packages/python` and `.github/workflows` ([PLAN.md](PLAN.md), Assumptions).

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | Where the language lives | `Language` enum and `Person.language` in swarm-models | A language type per package | One more field on a shared model |
| [D2](#d2) | How Python catalogues are read | `.po` files read with Babel, no `.mo` | Compiled `.mo` catalogues | Parsing at run time |
| [D3](#d3) | Where front-end messages live | One central set of JSON files in `packages/ts/i18n`, used through react-intl | Messages in each front end | One package every shell depends on |
| [D4](#d4) | How CI fails on a missing message | Steps in `python.yml` and `typescript.yml` | A new workflow | The steps sit in the jobs that exist |
| [D5](#d5) | An empty Python translation | English with a WARNING; unknown id raises | Raise on an empty translation | Degraded text instead of a stop |
| [D6](#d6) | Proof of the language switch | Vitest test of `I18nProvider`, no language control in the shells | A control in each shell and a Playwright check | Not driven end to end yet |
| [D7](#d7) | Where the frames get their words | Frames hold message ids and translate them | Shells pass translated labels | The `ui` package depends on react-intl |
| [D8](#d8) | Where `Language` is declared | New `swarm_models/models/enums.py` | The existing `enums/` folders | Two enum layouts in swarm-models |
| [D9](#d9) | Malformed `.po` lines | Lines checked before Babel reads | Trust Babel | An extra pattern to maintain |

## <a id="d1"></a>D1: Where the language lives

**Chosen:** `Language` in [`enums.py:8-21`](https://github.com/gpbcom/swarm/blob/a2e43f7e74d65cc12a43507ec33f673fd2bc62e3/packages/python/swarm-models/src/swarm_models/models/enums.py#L8-L21) and `Person.language` ([`person.py:48`](../../../backend/swarm-models/src/swarm_models/people/person.py#L48)) · **Source:** K09, [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ Shared enum and a field on `Person` | AGENT.md puts shared models in swarm-models and generates the schema, Rust and TypeScript from them ([`generated.rs:430`](../../../rust/swarm-models/src/generated.rs#L430)); `swarm-i18n` imports the same `Language` | The shared schema and two generated files change |
| A language type in each package | No change to swarm-models | Four languages written several times, against the single source rule |

**Trade-off:** one field on a shared model buys one definition of the four languages. Its default is English, and storing it in a database, Keycloak or a gateway endpoint is outside the ticket's area.

**Revisit when:** the ticket that stores people persists the language.

## <a id="d2"></a>D2: How Python catalogues are read

**Chosen:** `read_po` on the `.po` files ([`po_catalog_store.py:95`](../../../backend/swarm-storage/src/swarm_storage/shared/i18n/po_catalog_store.py#L95)) · **Source:** K15, [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ Read `.po` with Babel | No compiled `.mo` binary is committed ([PLAN.md](PLAN.md), Assumptions); the checker sees fuzzy and empty entries, which `.mo` hides | Parsed at run time |
| Compiled `.mo` | The usual gettext form | A binary in the repository, and a build step to keep in step |

**Trade-off:** parsing cost for readable, diffable catalogues. Each catalogue is read once and kept ([`translator.py:43-57`](../../../backend/swarm-service/src/swarm_service/shared/i18n/translator.py#L43-L57)).

**Revisit when:** start-up time of a service is shown to depend on reading catalogues. No measurement was made.

## <a id="d3"></a>D3: Where front-end messages live

**Chosen:** `packages/ts/i18n/src/messages/<lang>.json` ([`catalogues.ts:9`](../../../frontend/packages/i18n/src/catalogues.ts#L9)), used through react-intl ([`i18n-provider.tsx:36`](../../../frontend/packages/i18n/src/i18n-provider.tsx#L36)) · **Source:** K10, K11, [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ One central package | One `check-messages` covers every front end ([`check-messages.ts`](../../../frontend/packages/i18n/scripts/check-messages.ts)); the frames of `packages/ts/ui` share the words | Every shell depends on it |
| Messages inside each front end | Each shell is self-contained | One check per shell, and the shared frames cannot own their words |

**Trade-off:** coupling of the shells to one package for one check and one set of words.

**Revisit when:** a front end needs messages no other front end shares in large numbers.

## <a id="d4"></a>D4: How CI fails on a missing message

**Chosen:** a step in `python.yml` ([`python.yml:182-183`](../../../.github/workflows/python.yml#L182-L183)) and in `typescript.yml` ([`typescript.yml:45-46`](../../../.github/workflows/typescript.yml#L45-L46)) · **Source:** K12, [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ Steps in the existing workflows | `detect_changes.py` already runs every check when `packages/` changes ([PLAN.md](PLAN.md)); the TypeScript step uses `--if-present`, so only projects with the script run it | The check is not visible as its own workflow |
| A new workflow | A separate status | A second detection of what changed |

**Trade-off:** no separate status for the check, in return for no new detection logic.

**Revisit when:** the check needs to be a required status on its own.

## <a id="d5"></a>D5: An empty Python translation

**Chosen:** fall back to English with a WARNING, and raise `SECatalogUnknownMessageError` for an id not in the template ([`translator.py:93-104`](../../../backend/swarm-service/src/swarm_service/shared/i18n/translator.py#L93-L104)) · **Source:** K16, [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ English fallback, error on unknown id | A person still reads something; AGENT.md reserves WARNING for a degraded result the code recovers from; a wrong id is a bug and fails loudly | A person may see English |
| Raise on any missing text | Nothing untranslated is ever shown | A runtime failure for a gap CI already catches |

**Trade-off:** degraded text instead of a stop, because the CI check ([D4](#d4)) is the gate.

**Revisit when:** a Client is shown untranslated text in production.

## <a id="d6"></a>D6: Proof of the language switch

**Chosen:** the Vitest test of `I18nProvider` ([`i18n-provider.test.tsx:58-74`](../../../frontend/packages/i18n/test/i18n-provider.test.tsx#L58-L74)); the shells are wired but get no language control · **Source:** K11, K18, [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ Package-level test | The control belongs to the UC-023 A3 and UC-015 A2 screens of later tickets ([PLAN.md](PLAN.md)); the shells stay empty frames | The switch is not driven in a real shell |
| A control in each shell, with a Playwright check | Proves it end to end | Adds a screen state this ticket does not own, so TKT-21 capture would apply |

**Trade-off:** the switch is proved at the provider, not in the browser.

**Revisit when:** the language screens of UC-023 and UC-015 are built.

## <a id="d7"></a>D7: Where the frames get their words

**Chosen:** `parts.ts` holds `messageId`s ([`parts.ts:21-24`](../../../frontend/packages/ui/src/frames/parts.ts#L21-L24)) and the frames call `intl.formatMessage` ([`SideBar.tsx:26`](../../../frontend/packages/ui/src/frames/shell/SideBar.tsx#L26)) · **Source:** K18, K20, read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Frames translate their ids | Each shell changes only its root and status bar | `packages/ts/ui` needs react-intl ([`package.json`](../../../frontend/packages/ui/package.json)) and an `IntlProvider` above it |
| Shells pass translated labels | The frames stay free of react-intl | Every shell repeats the same lookups |

**Trade-off:** the reason was not recorded by the workers. The diff shows the first option; treat it as an open point.

**Revisit when:** a frame is used where no `I18nProvider` exists.

## <a id="d8"></a>D8: Where `Language` is declared

**Chosen:** a new `models/enums.py` in swarm-models ([`enums.py`](https://github.com/gpbcom/swarm/blob/a2e43f7e74d65cc12a43507ec33f673fd2bc62e3/packages/python/swarm-models/src/swarm_models/models/enums.py)) · **Source:** [PLAN.md](PLAN.md)

| Option | For | Against |
| --- | --- | --- |
| ✅ One `enums.py` | CLAUDE.md: all enums of a module are in one `enums.py` at the root of its `models` | The existing `enums/` folders of swarm-models are not migrated |
| Add to an `enums/` folder | Matches the neighbours | Breaks the rule for new code |

**Trade-off:** two layouts coexist in swarm-models; migration is a follow-up the plan names.

**Revisit when:** the existing `enums/` folders are migrated.

## <a id="d9"></a>D9: Malformed `.po` lines

**Chosen:** `LINE_PATTERN` checked before `read_po` ([`po_catalog_store.py:47`](../../../backend/swarm-storage/src/swarm_storage/shared/i18n/po_catalog_store.py#L47), [`po_catalog_store.py:57-74`](../../../backend/swarm-storage/src/swarm_storage/shared/i18n/po_catalog_store.py#L57-L74)) · **Source:** K15, read from the diff

| Option | For | Against |
| --- | --- | --- |
| ✅ Pre-check lines | The code's own note says Babel accepts an unterminated string without a word, so a broken catalogue would pass the check | A regular expression to keep in step with the `.po` syntax |
| Trust Babel | Less code | A silently accepted malformed file |

**Trade-off:** a small pattern for an exit code 2 on a bad catalogue ([`check_catalogs.py:30-32`](https://github.com/gpbcom/swarm/blob/a2e43f7e74d65cc12a43507ec33f673fd2bc62e3/packages/python/swarm-i18n/src/swarm_i18n/api/cli/check_catalogs.py#L30-L32)).

**Revisit when:** Babel rejects such lines itself.

## 📝 Assumptions behind the choices

- The shells show no use case state and take only translated labels: supports [D6](#d6) and [D7](#d7).
- The French, German and Spanish texts were proposed by agents and await the product owner's review (T1.35): supports [D3](#d3).
