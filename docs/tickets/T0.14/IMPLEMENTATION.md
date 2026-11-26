# T0.14: Implementation choices

**Ticket:** [TICKET.md](TICKET.md) · **How it works:** [EXPLAIN.md](EXPLAIN.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🎯 Constraints

- A token changed on the visual identity page reaches the apps and the mock-ups in one build (criterion 1 of [TICKET.md](TICKET.md)).
- The four shells open in light and dark mode, and the Tauri 2 shell builds on three systems (criteria 2 and 3 of [TICKET.md](TICKET.md)).
- Components use the tokens only, never a value of their own (design system section of the technical page, quoted in [TICKET.md](TICKET.md)).
- TypeScript is strict, and eslint forbids non-null assertions (the strict `@swarm/config` base, [`frontend/apps/back-office/src/main.tsx:8`](../../../frontend/apps/back-office/src/main.tsx#L8)).
- The ticket owns its own files only, and no language support yet: that is T0.15 ([TICKET.md](TICKET.md), out of scope).

## ⚖️ Choices at a glance

| # | Decision | Chosen | Main alternative | Trade-off accepted |
| --- | --- | --- | --- | --- |
| [D1](#d1) | Where words on screen live | `as const` data in `parts.ts` | Messages from the i18n package | T0.15 must still convert them |
| [D2](#d2) | Strict CSP of the desktop shell | `'self'` only | Allow `'unsafe-inline'` styles | Radix run-time styles may be blocked |
| [D3](#d3) | Tauri and tauri-build versions | Exact pins | Caret ranges or the newest 2.x | Patches wait for a manual raise |
| [D4](#d4) | Assembling the desktop pages | `node:fs` script with checks | Shell copy or a dependency | More code than a one-liner |
| [D5](#d5) | Missing `#root` in an app | Throw a typed `Error` | Non-null assertion | A few more lines per app |
| [D6](#d6) | Side bar items | `<button>` elements | Anchors or role divs | Needs a CSS reset |
| [D7](#d7) | Optional props typing | `T \| undefined` explicit | Build props conditionally | API slightly looser |
| [D8](#d8) | Title bar separators | Text nodes from a `trail` array | CSS separators | A Fragment per entry |
| [D9](#d9) | Client portal Alarms item | One list with `siteAgentOnly`, default false | Two lists | Default shows fewer items |
| [D10](#d10) | Linux libraries of the desktop job | Drop `libappindicator3-dev` | Ayatana replacement | A tray icon needs the package later |
| [D11](#d11) | Clippy lints of the desktop crate | Plain strings | Tables with priority | Differs from the Rust workspace style |
| [D12](#d12) | Tauri icon | Flat primary-colour square | Draw a logo, keep all generated icons | No brand icon yet |
| [D13](#d13) | Where the documentation sits | Paragraphs after existing blocks | Table rows, new section | Less scannable than a table |
| [D14](#d14) | Aid for Vite types and test casts | `vite/client` in tsconfig types | A `vite-env.d.ts` per app | Pulls in all Vite client types |

## <a id="d1"></a>D1: Where words on screen live

**Chosen:** all on-screen words as `as const satisfies readonly NavItem[]` data · **Where:** [`frontend/packages/ui/src/frames/parts.ts:1`](../../../frontend/packages/ui/src/frames/parts.ts#L1) · **Source:** K16

| Option | For | Against |
| --- | --- | --- |
| ✅ Data in `parts.ts` | One place for T0.15 to turn into messages. Keeps literal types for the default `active` id | Words are still plain English until T0.15 |
| Inline strings in each frame | Least code | Words spread over five files |
| Messages from the i18n package | Final shape of BR-017 | The i18n package is not available yet |

**Trade-off:** T0.15 has one file to convert. **Revisit when:** T0.15 lands.

## <a id="d2"></a>D2: Strict CSP of the desktop shell

**Chosen:** `'self'` only, no `'unsafe-inline'` · **Where:** [`frontend/apps/desktop/src-tauri/tauri.conf.json:28`](../../../frontend/apps/desktop/src-tauri/tauri.conf.json#L28) · **Source:** K21

| Option | For | Against |
| --- | --- | --- |
| ✅ Strict | Safest | May block inline styles Radix sets at run time, which could not be checked without a display |
| `'unsafe-inline'` in `style-src` | Nothing blocked | Weakens the policy for every style |
| `style-src-attr 'unsafe-inline'` only | Narrow | Not needed yet; kept as the fallback |

**Trade-off:** safety first, with a known follow-up. **Revisit when:** the desktop first shows a Dialog (see the follow-up in [EXPLAIN.md](EXPLAIN.md)).

## <a id="d3"></a>D3: Tauri and tauri-build versions

**Chosen:** `tauri` `=2.12.6` (the CLI's version) and `tauri-build` `=2.7.6` · **Where:** [`frontend/apps/desktop/src-tauri/Cargo.toml:15`](../../../frontend/apps/desktop/src-tauri/Cargo.toml#L15) · **Source:** K21

| Option | For | Against |
| --- | --- | --- |
| ✅ Exact pins | Match the test, the lock file and the installed CLI | Miss the 2.12.7 patch until raised with the CLI |
| Tauri 2.12.7 | Newest | Differs from the CLI |
| Caret ranges | Automatic patches | The crate and CLI could drift apart |

**Trade-off:** manual raises. **Revisit when:** a Tauri patch is needed; raise crate and CLI together.

## <a id="d4"></a>D4: Assembling the desktop pages

**Chosen:** a script using only `node:fs`, checking each `dist/index.html` before deleting the old `dist` · **Where:** [`frontend/apps/desktop/scripts/assemble.ts:10-20`](../../../frontend/apps/desktop/scripts/assemble.ts#L10-L20) · **Source:** K21

| Option | For | Against |
| --- | --- | --- |
| ✅ `node:fs` script | Same on Windows, macOS and Linux, no new dependency, a missing build never empties `dist` | More code |
| Shell `cp -r` | One line | Not portable to Windows |
| `fs-extra` or `shx` | Short | A new dependency |

**Trade-off:** a little more code for portability. **Revisit when:** more apps join the desktop.

## <a id="d5"></a>D5: A missing `#root`

**Chosen:** `querySelector` then throw an `Error` · **Where:** [`frontend/apps/mission-studio/src/main.tsx:8`](../../../frontend/apps/mission-studio/src/main.tsx#L8), [`back-office`](../../../frontend/apps/back-office/src/main.tsx#L8), [`client-portal`](../../../frontend/apps/client-portal/src/main.tsx#L7), [`ground-control`](../../../frontend/apps/ground-control/src/main.tsx#L9) · **Source:** K17 to K20

| Option | For | Against |
| --- | --- | --- |
| ✅ Throw | Strictly typed, passes eslint, clear message on a broken `index.html` | A few lines per app |
| `getElementById('root')!` | Shortest | Forbidden by the strict eslint config |
| Cast to `HTMLElement` or silent return | Short | Hides the failure |

For Ground control, the K08 test checks that the source contains `#root`, so `querySelector('#root')` was used there (K17). The mixed forms are a follow-up.

**Trade-off:** more lines for a loud failure. **Revisit when:** the four apps share one bootstrap.

## <a id="d6"></a>D6: Side bar items

**Chosen:** `<button type="button">` with `nav-item` and `aria-current` · **Where:** [`frontend/packages/ui/src/frames/shell/SideBar.tsx:17-25`](../../../frontend/packages/ui/src/frames/shell/SideBar.tsx#L17-L25) · **Source:** K16

| Option | For | Against |
| --- | --- | --- |
| ✅ Buttons | Keyboard access, matches the brief "items are buttons" | A CSS reset in `frames.css` |
| Anchors | Semantic for links | Items are not links yet |
| Divs with a role | Free styling | Keyboard handling to write |

**Trade-off:** a reset. **Revisit when:** items become routes.

## <a id="d7"></a>D7: Optional props typing

**Chosen:** `T | undefined` written explicitly · **Where:** [`frontend/packages/ui/src/frames/shell/SideBar.tsx:8`](../../../frontend/packages/ui/src/frames/shell/SideBar.tsx#L8) · **Source:** K16

| Option | For | Against |
| --- | --- | --- |
| ✅ Explicit `undefined` | Frames pass optional props straight through. Strict tsconfig unchanged | API slightly looser |
| Build props conditionally | Tight types | Noise in each frame |
| Turn off `exactOptionalPropertyTypes` | Simple | Weakens the shared strict config |

**Trade-off:** looser API. **Revisit when:** the props are reworked.

## <a id="d8"></a>D8: Title bar separators

**Chosen:** a `trail` array joined with " · " text nodes · **Where:** [`frontend/packages/ui/src/frames/shell/TitleBar.tsx:14-23`](../../../frontend/packages/ui/src/frames/shell/TitleBar.tsx#L14-L23) · **Source:** K16

| Option | For | Against |
| --- | --- | --- |
| ✅ Text nodes | One path for all five parts, visible to tests and screen readers | A Fragment per entry |
| Hand-written separators | None | Repeated in each frame |
| CSS separators | No extra nodes | Invisible to tests and screen readers |

**Trade-off:** extra nodes. **Revisit when:** the title bar needs another layout.

## <a id="d9"></a>D9: Client portal Alarms item

**Chosen:** one list filtered by `siteAgentOnly`, `isSiteAgent` default false · **Where:** [`frontend/packages/ui/src/frames/apps/ClientPortalFrame.tsx:28-30`](../../../frontend/packages/ui/src/frames/apps/ClientPortalFrame.tsx#L28-L30) · **Source:** K16

| Option | For | Against |
| --- | --- | --- |
| ✅ One list with a flag | As the brief says. Conservative default | Default hides an item |
| Two lists | Explicit | Duplication |
| Always show Alarms | Simple | Wrong for other personas |

**Trade-off:** the fewest items by default. **Revisit when:** sign-in (T0.11) supplies the persona.

## <a id="d10"></a>D10: Linux libraries of the desktop job

**Chosen:** drop `libappindicator3-dev`, no replacement · **Where:** [`.github/workflows/desktop.yml:57`](../../../.github/workflows/desktop.yml#L57) · **Source:** K11 (review round 2)

| Option | For | Against |
| --- | --- | --- |
| ✅ Drop it | `ubuntu-latest` (24.04 and later) no longer ships it. The shell has no tray icon. Faster install | A tray icon later needs a package |
| `libayatana-appindicator3-dev` | Keeps a tray option | Not needed now |

**Trade-off:** none today. **Revisit when:** a tray icon is added. A test that the package does not return is a follow-up.

## <a id="d11"></a>D11: Clippy lints of the desktop crate

**Chosen:** `all = "deny"`, `pedantic = "warn"` as plain strings · **Where:** [`frontend/apps/desktop/src-tauri/Cargo.toml:23`](../../../frontend/apps/desktop/src-tauri/Cargo.toml#L23) · **Source:** K21

| Option | For | Against |
| --- | --- | --- |
| ✅ Plain strings | The K03 test compares the lints to exactly these values. No overrides, so no priority conflict | Differs from the style of [`rust/Cargo.toml`](../../../rust/Cargo.toml) |
| Tables with `priority = -1` | Same style as the workspace | Would fail the test |

**Trade-off:** same behaviour, different spelling. **Revisit when:** the crate needs a lint override.

## <a id="d12"></a>D12: Tauri icon

**Chosen:** a flat `#4338ca` square (token `color.primary`), extra generated icons deleted · **Where:** [`frontend/apps/desktop/src-tauri/icons/icon.png`](../../../frontend/apps/desktop/src-tauri/icons/icon.png) · **Source:** K21

| Option | For | Against |
| --- | --- | --- |
| ✅ Flat square | No invented logo. Only the files of the brief | Mobile icons need regeneration if mobile targets come |
| Keep every generated icon | Complete | Files outside the brief |
| Draw a logo | Branded | A design nobody specified (TKT-8) |

**Trade-off:** no brand icon. **Revisit when:** a logo is specified.

## <a id="d13"></a>D13: Where the documentation sits

**Chosen:** paragraphs after existing blocks of [`AGENT.md`](../../../AGENT.md#L21-L27), a paragraph in its Mono-repo section and one in [`README.md`](../../../README.md#L292-L295) · **Source:** K22

| Option | For | Against |
| --- | --- | --- |
| ✅ Paragraphs | Follow the style of the `packages/python` paragraph. No new rows or section | Harder to scan than a table |
| Table rows or bullets | Easier to scan | Rows to add to a path table |
| A new README section | Visible | A larger change to the layout |

**Trade-off:** scanning. **Revisit when:** the front-end section grows. The rewrap of long lines is a follow-up.

## <a id="d14"></a>D14: Vite types and test casts

**Chosen:** `"vite/client"` in `compilerOptions.types` of each app · **Where:** [`frontend/apps/mission-studio/tsconfig.json:8`](../../../frontend/apps/mission-studio/tsconfig.json#L8) · **Source:** K10. In the tests (K08) the `?? ''` was dropped for `active[0]?.textContent.trim()` ([`frontend/apps/ground-control/test/app.test.tsx`](../../../frontend/apps/ground-control/test/app.test.tsx)); the guard in [`frontend/packages/ui/test/frames.test.tsx:205-207`](../../../frontend/packages/ui/test/frames.test.tsx#L205-L207) throws a clear error when a button is missing (K07).

| Option | For | Against |
| --- | --- | --- |
| ✅ `types` entry | One line in a file the task owns. Vite is already a dependency | Pulls in all Vite client types |
| `src/vite-env.d.ts` per app | Narrow | A file the task does not own |

**Trade-off:** broader ambient types. **Revisit when:** an app needs fewer ambient types.

## 📝 Assumptions behind the choices

- No feature or use case is linked, and BR-017 only through the epic: supports [D1](#d1).
- `➖ No screen`, the shells are empty frames: supports [D6](#d6) and [D8](#d8).
- Open point: the reason for placing the tokens in a separate package, rather than reading `visual-identity.css` directly, is the ticket's own text ([TICKET.md](TICKET.md)); no worker reported an alternative.
