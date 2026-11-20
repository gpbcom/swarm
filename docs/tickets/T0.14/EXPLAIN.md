# T0.14: Design tokens, components and app shells

**Status:** ✅ Done · **Ticket:** [TICKET.md](TICKET.md) · **Choices and trade-offs:** [IMPLEMENTATION.md](IMPLEMENTATION.md) · **Review:** [REVIEW.md](REVIEW.md)

## 🔭 What it does

- One build of the visual identity now also writes the design tokens for the front ends, with light and dark values.
- A shared component package offers the components of the component sheet and the frame of each part of Swarm (title bar, side bar, status bar).
- Four empty shells (Ground control, Mission studio, Back office, Client portal) open with their frame in light and dark mode.
- A Tauri 2 desktop shell wraps Ground control and Mission studio, and a workflow builds it on Windows, macOS and Linux.

## ⚙️ How it works

1. **Tokens are generated:** `specs.py build` already wrote the CSS of the visual identity. It now also writes the same text to the tokens package, in [`.claude/skills/write-specs/scripts/specs.py:137-139`](../../../.claude/skills/write-specs/scripts/specs.py#L137-L139), at the path named in [`.claude/skills/write-specs/scripts/spec_model.py:18`](../../../.claude/skills/write-specs/scripts/spec_model.py#L18). The package exposes it as `@swarm/tokens/tokens.css` in [`packages/ts/tokens/package.json:5-7`](../../../packages/ts/tokens/package.json#L5-L7), and the generated file is [`packages/ts/tokens/src/tokens.css`](../../../packages/ts/tokens/src/tokens.css) (light values in `:root`, dark values under `prefers-color-scheme: dark`).
2. **Components use the tokens only:** the stylesheets of [`packages/ts/ui/src/styles.css`](../../../packages/ts/ui/src/styles.css) read `var(--...)` values. The components sit on Radix primitives and are exported by one barrel, [`packages/ts/ui/src/index.ts:1-6`](../../../packages/ts/ui/src/index.ts#L1-L6): layout, controls, overlays, feedback, data and frames.
3. **A frame is three parts and a window:** [`packages/ts/ui/src/frames/Window.tsx:10-20`](../../../packages/ts/ui/src/frames/Window.tsx#L10-L20) places the title bar, the side bar, the content and the status bar. The title bar joins the part name and its context with " · " and puts its actions after a spacer ([`TitleBar.tsx:13-31`](../../../packages/ts/ui/src/frames/TitleBar.tsx#L13-L31)). The side bar renders one button per item and marks the active one with `aria-current` ([`SideBar.tsx:11-30`](../../../packages/ts/ui/src/frames/SideBar.tsx#L11-L30)). The status bar joins its items ([`StatusBar.tsx:8-18`](../../../packages/ts/ui/src/frames/StatusBar.tsx#L8-L18)).
4. **Each part has its frame and its words:** the names and navigation items are data in [`packages/ts/ui/src/frames/parts.ts:11-19`](../../../packages/ts/ui/src/frames/parts.ts#L11-L19). [`ClientPortalFrame.tsx:28-30`](../../../packages/ts/ui/src/frames/ClientPortalFrame.tsx#L28-L30) hides the items flagged `siteAgentOnly` unless `isSiteAgent` is true. [`GroundControlFrame.tsx`](../../../packages/ts/ui/src/frames/GroundControlFrame.tsx) always shows Hold and Abort in its title bar.
5. **A shell loads both stylesheets and renders its frame:** [`frontends/ground-control/src/main.tsx:1-18`](../../../frontends/ground-control/src/main.tsx#L1-L18) imports the tokens and the UI styles, finds `#root` (it throws if missing, lines [9-12](../../../frontends/ground-control/src/main.tsx#L9-L12)) and renders `App`. [`frontends/ground-control/src/App.tsx:5`](../../../frontends/ground-control/src/App.tsx#L5) renders the frame with two no-op handlers. The three other shells follow the same shape: [`mission-studio`](../../../frontends/mission-studio/src/App.tsx), [`back-office`](../../../frontends/back-office/src/App.tsx) and [`client-portal`](../../../frontends/client-portal/src/App.tsx).
6. **The desktop shell serves two built apps:** `beforeBuildCommand` builds Ground control and Mission studio, then runs the assembler ([`tauri.conf.json:7`](../../../frontends/desktop/src-tauri/tauri.conf.json#L7)). [`assemble.ts:11-24`](../../../frontends/desktop/scripts/assemble.ts#L11-L24) checks each `dist/index.html`, then replaces `dist/` with one folder per app. The two windows and the strict content security policy are declared in [`tauri.conf.json:10-29`](../../../frontends/desktop/src-tauri/tauri.conf.json#L10-L29). Rust only starts the runtime, in [`lib.rs:10-14`](../../../frontends/desktop/src-tauri/src/lib.rs#L10-L14).
7. **CI builds it on three systems:** [`.github/workflows/desktop.yml:35-61`](../../../.github/workflows/desktop.yml#L35-L61) runs a matrix of Ubuntu, Windows and macOS, installs the Linux libraries on Ubuntu only, installs with the frozen lock file and runs `tauri build --no-bundle`. The Ubuntu job also runs `cargo fmt` and `cargo clippy`.

## 🧱 Files and lines changed

<!-- changes -->
| File | Change | Lines in the new version | Added | Removed |
| --- | --- | --- | --- | --- |
| [`.claude/rules/enforcement.json`](../../../.claude/rules/enforcement.json) | Modified | [135-139](../../../.claude/rules/enforcement.json#L135) | +5 | −0 |
| [`.claude/rules/specs.md`](../../../.claude/rules/specs.md) | Modified | [340-341](../../../.claude/rules/specs.md#L340), [348](../../../.claude/rules/specs.md#L348), [401-403](../../../.claude/rules/specs.md#L401) | +6 | −4 |
| [`.claude/skills/write-specs/SKILL.md`](../../../.claude/skills/write-specs/SKILL.md) | Modified | [25](../../../.claude/skills/write-specs/SKILL.md#L25), [67](../../../.claude/skills/write-specs/SKILL.md#L67) | +2 | −2 |
| [`.claude/skills/write-specs/scripts/spec_check.py`](../../../.claude/skills/write-specs/scripts/spec_check.py) | Modified | [11](../../../.claude/skills/write-specs/scripts/spec_check.py#L11), [100-101](../../../.claude/skills/write-specs/scripts/spec_check.py#L100) | +3 | −1 |
| [`.claude/skills/write-specs/scripts/spec_model.py`](../../../.claude/skills/write-specs/scripts/spec_model.py) | Modified | [18](../../../.claude/skills/write-specs/scripts/spec_model.py#L18) | +1 | −0 |
| [`.claude/skills/write-specs/scripts/specs.py`](../../../.claude/skills/write-specs/scripts/specs.py) | Modified | [17](../../../.claude/skills/write-specs/scripts/specs.py#L17), [31](../../../.claude/skills/write-specs/scripts/specs.py#L31), [137-139](../../../.claude/skills/write-specs/scripts/specs.py#L137) | +5 | −2 |
| [`.github/workflows/automerge.yml`](../../../.github/workflows/automerge.yml) | Modified | [12](../../../.github/workflows/automerge.yml#L12) | +1 | −1 |
| [`.github/workflows/desktop.yml`](../../../.github/workflows/desktop.yml) | Added | [1-69](../../../.github/workflows/desktop.yml#L1) | +69 | −0 |
| [`.gitignore`](../../../.gitignore) | Modified | [44-46](../../../.gitignore#L44) | +3 | −0 |
| [`README.md`](../../../README.md) | Modified | [287](../../../README.md#L287), [292-296](../../../README.md#L292) | +6 | −1 |
| `frontends/.gitkeep` | Deleted | ➖ deleted | +0 | −0 |
| [`frontends/back-office/eslint.config.js`](../../../frontends/back-office/eslint.config.js) | Added | [1-11](../../../frontends/back-office/eslint.config.js#L1) | +11 | −0 |
| [`frontends/back-office/index.html`](../../../frontends/back-office/index.html) | Added | [1-13](../../../frontends/back-office/index.html#L1) | +13 | −0 |
| [`frontends/back-office/package.json`](../../../frontends/back-office/package.json) | Added | [1-34](../../../frontends/back-office/package.json#L1) | +34 | −0 |
| [`frontends/back-office/src/App.tsx`](../../../frontends/back-office/src/App.tsx) | Added | [1-6](../../../frontends/back-office/src/App.tsx#L1) | +6 | −0 |
| [`frontends/back-office/src/main.tsx`](../../../frontends/back-office/src/main.tsx) | Added | [1-17](../../../frontends/back-office/src/main.tsx#L1) | +17 | −0 |
| [`frontends/back-office/test/app.test.tsx`](../../../frontends/back-office/test/app.test.tsx) | Added | [1-71](../../../frontends/back-office/test/app.test.tsx#L1) | +71 | −0 |
| [`frontends/back-office/tsconfig.json`](../../../frontends/back-office/tsconfig.json) | Added | [1-25](../../../frontends/back-office/tsconfig.json#L1) | +25 | −0 |
| [`frontends/back-office/vite.config.ts`](../../../frontends/back-office/vite.config.ts) | Added | [1-12](../../../frontends/back-office/vite.config.ts#L1) | +12 | −0 |
| [`frontends/client-portal/eslint.config.js`](../../../frontends/client-portal/eslint.config.js) | Added | [1-11](../../../frontends/client-portal/eslint.config.js#L1) | +11 | −0 |
| [`frontends/client-portal/index.html`](../../../frontends/client-portal/index.html) | Added | [1-13](../../../frontends/client-portal/index.html#L1) | +13 | −0 |
| [`frontends/client-portal/package.json`](../../../frontends/client-portal/package.json) | Added | [1-34](../../../frontends/client-portal/package.json#L1) | +34 | −0 |
| [`frontends/client-portal/src/App.tsx`](../../../frontends/client-portal/src/App.tsx) | Added | [1-7](../../../frontends/client-portal/src/App.tsx#L1) | +7 | −0 |
| [`frontends/client-portal/src/main.tsx`](../../../frontends/client-portal/src/main.tsx) | Added | [1-17](../../../frontends/client-portal/src/main.tsx#L1) | +17 | −0 |
| [`frontends/client-portal/test/app.test.tsx`](../../../frontends/client-portal/test/app.test.tsx) | Added | [1-76](../../../frontends/client-portal/test/app.test.tsx#L1) | +76 | −0 |
| [`frontends/client-portal/tsconfig.json`](../../../frontends/client-portal/tsconfig.json) | Added | [1-25](../../../frontends/client-portal/tsconfig.json#L1) | +25 | −0 |
| [`frontends/client-portal/vite.config.ts`](../../../frontends/client-portal/vite.config.ts) | Added | [1-12](../../../frontends/client-portal/vite.config.ts#L1) | +12 | −0 |
| [`frontends/desktop/eslint.config.js`](../../../frontends/desktop/eslint.config.js) | Added | [1-11](../../../frontends/desktop/eslint.config.js#L1) | +11 | −0 |
| [`frontends/desktop/package.json`](../../../frontends/desktop/package.json) | Added | [1-19](../../../frontends/desktop/package.json#L1) | +19 | −0 |
| [`frontends/desktop/scripts/assemble.ts`](../../../frontends/desktop/scripts/assemble.ts) | Added | [1-24](../../../frontends/desktop/scripts/assemble.ts#L1) | +24 | −0 |
| [`frontends/desktop/src-tauri/Cargo.lock`](../../../frontends/desktop/src-tauri/Cargo.lock) | Added | [1-4574](../../../frontends/desktop/src-tauri/Cargo.lock#L1) | +4574 | −0 |
| [`frontends/desktop/src-tauri/Cargo.toml`](../../../frontends/desktop/src-tauri/Cargo.toml) | Added | [1-27](../../../frontends/desktop/src-tauri/Cargo.toml#L1) | +27 | −0 |
| [`frontends/desktop/src-tauri/build.rs`](../../../frontends/desktop/src-tauri/build.rs) | Added | [1-5](../../../frontends/desktop/src-tauri/build.rs#L1) | +5 | −0 |
| [`frontends/desktop/src-tauri/capabilities/default.json`](../../../frontends/desktop/src-tauri/capabilities/default.json) | Added | [1-7](../../../frontends/desktop/src-tauri/capabilities/default.json#L1) | +7 | −0 |
| [`frontends/desktop/src-tauri/icons/128x128.png`](../../../frontends/desktop/src-tauri/icons/128x128.png) | Added | binary | +- | −- |
| [`frontends/desktop/src-tauri/icons/128x128@2x.png`](../../../frontends/desktop/src-tauri/icons/128x128@2x.png) | Added | binary | +- | −- |
| [`frontends/desktop/src-tauri/icons/32x32.png`](../../../frontends/desktop/src-tauri/icons/32x32.png) | Added | binary | +- | −- |
| [`frontends/desktop/src-tauri/icons/icon.icns`](../../../frontends/desktop/src-tauri/icons/icon.icns) | Added | binary | +- | −- |
| [`frontends/desktop/src-tauri/icons/icon.ico`](../../../frontends/desktop/src-tauri/icons/icon.ico) | Added | binary | +- | −- |
| [`frontends/desktop/src-tauri/icons/icon.png`](../../../frontends/desktop/src-tauri/icons/icon.png) | Added | binary | +- | −- |
| [`frontends/desktop/src-tauri/rust-toolchain.toml`](../../../frontends/desktop/src-tauri/rust-toolchain.toml) | Added | [1-3](../../../frontends/desktop/src-tauri/rust-toolchain.toml#L1) | +3 | −0 |
| [`frontends/desktop/src-tauri/src/lib.rs`](../../../frontends/desktop/src-tauri/src/lib.rs) | Added | [1-14](../../../frontends/desktop/src-tauri/src/lib.rs#L1) | +14 | −0 |
| [`frontends/desktop/src-tauri/src/main.rs`](../../../frontends/desktop/src-tauri/src/main.rs) | Added | [1-8](../../../frontends/desktop/src-tauri/src/main.rs#L1) | +8 | −0 |
| [`frontends/desktop/src-tauri/tauri.conf.json`](../../../frontends/desktop/src-tauri/tauri.conf.json) | Added | [1-42](../../../frontends/desktop/src-tauri/tauri.conf.json#L1) | +42 | −0 |
| [`frontends/desktop/tsconfig.json`](../../../frontends/desktop/tsconfig.json) | Added | [1-16](../../../frontends/desktop/tsconfig.json#L1) | +16 | −0 |
| [`frontends/ground-control/eslint.config.js`](../../../frontends/ground-control/eslint.config.js) | Added | [1-11](../../../frontends/ground-control/eslint.config.js#L1) | +11 | −0 |
| [`frontends/ground-control/index.html`](../../../frontends/ground-control/index.html) | Added | [1-13](../../../frontends/ground-control/index.html#L1) | +13 | −0 |
| [`frontends/ground-control/package.json`](../../../frontends/ground-control/package.json) | Added | [1-34](../../../frontends/ground-control/package.json#L1) | +34 | −0 |
| [`frontends/ground-control/src/App.tsx`](../../../frontends/ground-control/src/App.tsx) | Added | [1-6](../../../frontends/ground-control/src/App.tsx#L1) | +6 | −0 |
| [`frontends/ground-control/src/main.tsx`](../../../frontends/ground-control/src/main.tsx) | Added | [1-18](../../../frontends/ground-control/src/main.tsx#L1) | +18 | −0 |
| [`frontends/ground-control/test/app.test.tsx`](../../../frontends/ground-control/test/app.test.tsx) | Added | [1-83](../../../frontends/ground-control/test/app.test.tsx#L1) | +83 | −0 |
| [`frontends/ground-control/tsconfig.json`](../../../frontends/ground-control/tsconfig.json) | Added | [1-25](../../../frontends/ground-control/tsconfig.json#L1) | +25 | −0 |
| [`frontends/ground-control/vite.config.ts`](../../../frontends/ground-control/vite.config.ts) | Added | [1-12](../../../frontends/ground-control/vite.config.ts#L1) | +12 | −0 |
| [`frontends/mission-studio/eslint.config.js`](../../../frontends/mission-studio/eslint.config.js) | Added | [1-11](../../../frontends/mission-studio/eslint.config.js#L1) | +11 | −0 |
| [`frontends/mission-studio/index.html`](../../../frontends/mission-studio/index.html) | Added | [1-13](../../../frontends/mission-studio/index.html#L1) | +13 | −0 |
| [`frontends/mission-studio/package.json`](../../../frontends/mission-studio/package.json) | Added | [1-34](../../../frontends/mission-studio/package.json#L1) | +34 | −0 |
| [`frontends/mission-studio/src/App.tsx`](../../../frontends/mission-studio/src/App.tsx) | Added | [1-7](../../../frontends/mission-studio/src/App.tsx#L1) | +7 | −0 |
| [`frontends/mission-studio/src/main.tsx`](../../../frontends/mission-studio/src/main.tsx) | Added | [1-18](../../../frontends/mission-studio/src/main.tsx#L1) | +18 | −0 |
| [`frontends/mission-studio/test/app.test.tsx`](../../../frontends/mission-studio/test/app.test.tsx) | Added | [1-71](../../../frontends/mission-studio/test/app.test.tsx#L1) | +71 | −0 |
| [`frontends/mission-studio/tsconfig.json`](../../../frontends/mission-studio/tsconfig.json) | Added | [1-25](../../../frontends/mission-studio/tsconfig.json#L1) | +25 | −0 |
| [`frontends/mission-studio/vite.config.ts`](../../../frontends/mission-studio/vite.config.ts) | Added | [1-12](../../../frontends/mission-studio/vite.config.ts#L1) | +12 | −0 |
| [`packages/ts/tokens/package.json`](../../../packages/ts/tokens/package.json) | Added | [1-11](../../../packages/ts/tokens/package.json#L1) | +11 | −0 |
| [`packages/ts/tokens/src/tokens.css`](../../../packages/ts/tokens/src/tokens.css) | Added | [1-105](../../../packages/ts/tokens/src/tokens.css#L1) | +105 | −0 |
| [`packages/ts/ui/eslint.config.js`](../../../packages/ts/ui/eslint.config.js) | Added | [1-11](../../../packages/ts/ui/eslint.config.js#L1) | +11 | −0 |
| [`packages/ts/ui/package.json`](../../../packages/ts/ui/package.json) | Added | [1-45](../../../packages/ts/ui/package.json#L1) | +45 | −0 |
| [`packages/ts/ui/src/base.css`](../../../packages/ts/ui/src/base.css) | Added | [1-22](../../../packages/ts/ui/src/base.css#L1) | +22 | −0 |
| [`packages/ts/ui/src/controls/Button.tsx`](../../../packages/ts/ui/src/controls/Button.tsx) | Added | [1-11](../../../packages/ts/ui/src/controls/Button.tsx#L1) | +11 | −0 |
| [`packages/ts/ui/src/controls/Field.tsx`](../../../packages/ts/ui/src/controls/Field.tsx) | Added | [1-34](../../../packages/ts/ui/src/controls/Field.tsx#L1) | +34 | −0 |
| [`packages/ts/ui/src/controls/Tabs.tsx`](../../../packages/ts/ui/src/controls/Tabs.tsx) | Added | [1-39](../../../packages/ts/ui/src/controls/Tabs.tsx#L1) | +39 | −0 |
| [`packages/ts/ui/src/controls/controls.css`](../../../packages/ts/ui/src/controls/controls.css) | Added | [1-29](../../../packages/ts/ui/src/controls/controls.css#L1) | +29 | −0 |
| [`packages/ts/ui/src/controls/index.ts`](../../../packages/ts/ui/src/controls/index.ts) | Added | [1-6](../../../packages/ts/ui/src/controls/index.ts#L1) | +6 | −0 |
| [`packages/ts/ui/src/data/Card.tsx`](../../../packages/ts/ui/src/data/Card.tsx) | Added | [1-15](../../../packages/ts/ui/src/data/Card.tsx#L1) | +15 | −0 |
| [`packages/ts/ui/src/data/Conversation.tsx`](../../../packages/ts/ui/src/data/Conversation.tsx) | Added | [1-20](../../../packages/ts/ui/src/data/Conversation.tsx#L1) | +20 | −0 |
| [`packages/ts/ui/src/data/Kpis.tsx`](../../../packages/ts/ui/src/data/Kpis.tsx) | Added | [1-23](../../../packages/ts/ui/src/data/Kpis.tsx#L1) | +23 | −0 |
| [`packages/ts/ui/src/data/List.tsx`](../../../packages/ts/ui/src/data/List.tsx) | Added | [1-13](../../../packages/ts/ui/src/data/List.tsx#L1) | +13 | −0 |
| [`packages/ts/ui/src/data/Panels.tsx`](../../../packages/ts/ui/src/data/Panels.tsx) | Added | [1-13](../../../packages/ts/ui/src/data/Panels.tsx#L1) | +13 | −0 |
| [`packages/ts/ui/src/data/Table.tsx`](../../../packages/ts/ui/src/data/Table.tsx) | Added | [1-31](../../../packages/ts/ui/src/data/Table.tsx#L1) | +31 | −0 |
| [`packages/ts/ui/src/data/data.css`](../../../packages/ts/ui/src/data/data.css) | Added | [1-29](../../../packages/ts/ui/src/data/data.css#L1) | +29 | −0 |
| [`packages/ts/ui/src/data/index.ts`](../../../packages/ts/ui/src/data/index.ts) | Added | [1-12](../../../packages/ts/ui/src/data/index.ts#L1) | +12 | −0 |
| [`packages/ts/ui/src/feedback/Badge.tsx`](../../../packages/ts/ui/src/feedback/Badge.tsx) | Added | [1-18](../../../packages/ts/ui/src/feedback/Badge.tsx#L1) | +18 | −0 |
| [`packages/ts/ui/src/feedback/Banner.tsx`](../../../packages/ts/ui/src/feedback/Banner.tsx) | Added | [1-21](../../../packages/ts/ui/src/feedback/Banner.tsx#L1) | +21 | −0 |
| [`packages/ts/ui/src/feedback/Checklist.tsx`](../../../packages/ts/ui/src/feedback/Checklist.tsx) | Added | [1-31](../../../packages/ts/ui/src/feedback/Checklist.tsx#L1) | +31 | −0 |
| [`packages/ts/ui/src/feedback/EmptyState.tsx`](../../../packages/ts/ui/src/feedback/EmptyState.tsx) | Added | [1-17](../../../packages/ts/ui/src/feedback/EmptyState.tsx#L1) | +17 | −0 |
| [`packages/ts/ui/src/feedback/Progress.tsx`](../../../packages/ts/ui/src/feedback/Progress.tsx) | Added | [1-24](../../../packages/ts/ui/src/feedback/Progress.tsx#L1) | +24 | −0 |
| [`packages/ts/ui/src/feedback/Toast.tsx`](../../../packages/ts/ui/src/feedback/Toast.tsx) | Added | [1-34](../../../packages/ts/ui/src/feedback/Toast.tsx#L1) | +34 | −0 |
| [`packages/ts/ui/src/feedback/feedback.css`](../../../packages/ts/ui/src/feedback/feedback.css) | Added | [1-47](../../../packages/ts/ui/src/feedback/feedback.css#L1) | +47 | −0 |
| [`packages/ts/ui/src/feedback/index.ts`](../../../packages/ts/ui/src/feedback/index.ts) | Added | [1-12](../../../packages/ts/ui/src/feedback/index.ts#L1) | +12 | −0 |
| [`packages/ts/ui/src/frames/BackOfficeFrame.tsx`](../../../packages/ts/ui/src/frames/BackOfficeFrame.tsx) | Added | [1-34](../../../packages/ts/ui/src/frames/BackOfficeFrame.tsx#L1) | +34 | −0 |
| [`packages/ts/ui/src/frames/ClientPortalFrame.tsx`](../../../packages/ts/ui/src/frames/ClientPortalFrame.tsx) | Added | [1-40](../../../packages/ts/ui/src/frames/ClientPortalFrame.tsx#L1) | +40 | −0 |
| [`packages/ts/ui/src/frames/GroundControlFrame.tsx`](../../../packages/ts/ui/src/frames/GroundControlFrame.tsx) | Added | [1-56](../../../packages/ts/ui/src/frames/GroundControlFrame.tsx#L1) | +56 | −0 |
| [`packages/ts/ui/src/frames/MissionStudioFrame.tsx`](../../../packages/ts/ui/src/frames/MissionStudioFrame.tsx) | Added | [1-36](../../../packages/ts/ui/src/frames/MissionStudioFrame.tsx#L1) | +36 | −0 |
| [`packages/ts/ui/src/frames/SideBar.tsx`](../../../packages/ts/ui/src/frames/SideBar.tsx) | Added | [1-30](../../../packages/ts/ui/src/frames/SideBar.tsx#L1) | +30 | −0 |
| [`packages/ts/ui/src/frames/StatusBar.tsx`](../../../packages/ts/ui/src/frames/StatusBar.tsx) | Added | [1-19](../../../packages/ts/ui/src/frames/StatusBar.tsx#L1) | +19 | −0 |
| [`packages/ts/ui/src/frames/SwarmAdministrationFrame.tsx`](../../../packages/ts/ui/src/frames/SwarmAdministrationFrame.tsx) | Added | [1-31](../../../packages/ts/ui/src/frames/SwarmAdministrationFrame.tsx#L1) | +31 | −0 |
| [`packages/ts/ui/src/frames/TitleBar.tsx`](../../../packages/ts/ui/src/frames/TitleBar.tsx) | Added | [1-32](../../../packages/ts/ui/src/frames/TitleBar.tsx#L1) | +32 | −0 |
| [`packages/ts/ui/src/frames/Window.tsx`](../../../packages/ts/ui/src/frames/Window.tsx) | Added | [1-21](../../../packages/ts/ui/src/frames/Window.tsx#L1) | +21 | −0 |
| [`packages/ts/ui/src/frames/frames.css`](../../../packages/ts/ui/src/frames/frames.css) | Added | [1-25](../../../packages/ts/ui/src/frames/frames.css#L1) | +25 | −0 |
| [`packages/ts/ui/src/frames/index.ts`](../../../packages/ts/ui/src/frames/index.ts) | Added | [1-20](../../../packages/ts/ui/src/frames/index.ts#L1) | +20 | −0 |
| [`packages/ts/ui/src/frames/parts.ts`](../../../packages/ts/ui/src/frames/parts.ts) | Added | [1-63](../../../packages/ts/ui/src/frames/parts.ts#L1) | +63 | −0 |
| [`packages/ts/ui/src/index.ts`](../../../packages/ts/ui/src/index.ts) | Added | [1-6](../../../packages/ts/ui/src/index.ts#L1) | +6 | −0 |
| [`packages/ts/ui/src/layout/Grid2.tsx`](../../../packages/ts/ui/src/layout/Grid2.tsx) | Added | [1-9](../../../packages/ts/ui/src/layout/Grid2.tsx#L1) | +9 | −0 |
| [`packages/ts/ui/src/layout/Mono.tsx`](../../../packages/ts/ui/src/layout/Mono.tsx) | Added | [1-9](../../../packages/ts/ui/src/layout/Mono.tsx#L1) | +9 | −0 |
| [`packages/ts/ui/src/layout/Muted.tsx`](../../../packages/ts/ui/src/layout/Muted.tsx) | Added | [1-9](../../../packages/ts/ui/src/layout/Muted.tsx#L1) | +9 | −0 |
| [`packages/ts/ui/src/layout/Row.tsx`](../../../packages/ts/ui/src/layout/Row.tsx) | Added | [1-9](../../../packages/ts/ui/src/layout/Row.tsx#L1) | +9 | −0 |
| [`packages/ts/ui/src/layout/Spacer.tsx`](../../../packages/ts/ui/src/layout/Spacer.tsx) | Added | [1-9](../../../packages/ts/ui/src/layout/Spacer.tsx#L1) | +9 | −0 |
| [`packages/ts/ui/src/layout/Stack.tsx`](../../../packages/ts/ui/src/layout/Stack.tsx) | Added | [1-9](../../../packages/ts/ui/src/layout/Stack.tsx#L1) | +9 | −0 |
| [`packages/ts/ui/src/layout/index.ts`](../../../packages/ts/ui/src/layout/index.ts) | Added | [1-6](../../../packages/ts/ui/src/layout/index.ts#L1) | +6 | −0 |
| [`packages/ts/ui/src/layout/layout.css`](../../../packages/ts/ui/src/layout/layout.css) | Added | [1-6](../../../packages/ts/ui/src/layout/layout.css#L1) | +6 | −0 |
| [`packages/ts/ui/src/overlays/Dialog.tsx`](../../../packages/ts/ui/src/overlays/Dialog.tsx) | Added | [1-27](../../../packages/ts/ui/src/overlays/Dialog.tsx#L1) | +27 | −0 |
| [`packages/ts/ui/src/overlays/index.ts`](../../../packages/ts/ui/src/overlays/index.ts) | Added | [1-2](../../../packages/ts/ui/src/overlays/index.ts#L1) | +2 | −0 |
| [`packages/ts/ui/src/overlays/overlays.css`](../../../packages/ts/ui/src/overlays/overlays.css) | Added | [1-17](../../../packages/ts/ui/src/overlays/overlays.css#L1) | +17 | −0 |
| [`packages/ts/ui/src/styles.css`](../../../packages/ts/ui/src/styles.css) | Added | [1-7](../../../packages/ts/ui/src/styles.css#L1) | +7 | −0 |
| [`packages/ts/ui/test/controls.test.tsx`](../../../packages/ts/ui/test/controls.test.tsx) | Added | [1-128](../../../packages/ts/ui/test/controls.test.tsx#L1) | +128 | −0 |
| [`packages/ts/ui/test/data.test.tsx`](../../../packages/ts/ui/test/data.test.tsx) | Added | [1-86](../../../packages/ts/ui/test/data.test.tsx#L1) | +86 | −0 |
| [`packages/ts/ui/test/feedback.test.tsx`](../../../packages/ts/ui/test/feedback.test.tsx) | Added | [1-116](../../../packages/ts/ui/test/feedback.test.tsx#L1) | +116 | −0 |
| [`packages/ts/ui/test/frames.test.tsx`](../../../packages/ts/ui/test/frames.test.tsx) | Added | [1-317](../../../packages/ts/ui/test/frames.test.tsx#L1) | +317 | −0 |
| [`packages/ts/ui/test/layout.test.tsx`](../../../packages/ts/ui/test/layout.test.tsx) | Added | [1-43](../../../packages/ts/ui/test/layout.test.tsx#L1) | +43 | −0 |
| [`packages/ts/ui/test/overlays.test.tsx`](../../../packages/ts/ui/test/overlays.test.tsx) | Added | [1-52](../../../packages/ts/ui/test/overlays.test.tsx#L1) | +52 | −0 |
| [`packages/ts/ui/test/styles.test.ts`](../../../packages/ts/ui/test/styles.test.ts) | Added | [1-91](../../../packages/ts/ui/test/styles.test.ts#L1) | +91 | −0 |
| [`packages/ts/ui/tsconfig.json`](../../../packages/ts/ui/tsconfig.json) | Added | [1-25](../../../packages/ts/ui/tsconfig.json#L1) | +25 | −0 |
| [`packages/ts/ui/vitest.config.ts`](../../../packages/ts/ui/vitest.config.ts) | Added | [1-11](../../../packages/ts/ui/vitest.config.ts#L1) | +11 | −0 |
| [`tests/ci/workflows/test_desktop_workflow.py`](../../../tests/ci/workflows/test_desktop_workflow.py) | Added | [1-117](../../../tests/ci/workflows/test_desktop_workflow.py#L1) | +117 | −0 |
| [`tests/ci/workflows/test_gitflow_workflows.py`](../../../tests/ci/workflows/test_gitflow_workflows.py) | Modified | [12](../../../tests/ci/workflows/test_gitflow_workflows.py#L12) | +1 | −1 |
| [`tests/conventions/mono_repo/test_desktop_shell.py`](../../../tests/conventions/mono_repo/test_desktop_shell.py) | Added | [1-128](../../../tests/conventions/mono_repo/test_desktop_shell.py#L1) | +128 | −0 |
| [`tests/conventions/mono_repo/test_frontend_workspace.py`](../../../tests/conventions/mono_repo/test_frontend_workspace.py) | Added | [1-162](../../../tests/conventions/mono_repo/test_frontend_workspace.py#L1) | +162 | −0 |
| [`tests/harness/write_specs/helpers.py`](../../../tests/harness/write_specs/helpers.py) | Added | [1-51](../../../tests/harness/write_specs/helpers.py#L1) | +51 | −0 |
| [`tests/harness/write_specs/test_tokens_package.py`](../../../tests/harness/write_specs/test_tokens_package.py) | Added | [1-81](../../../tests/harness/write_specs/test_tokens_package.py#L1) | +81 | −0 |
| **127 files** | | | **+8242** | **−12** |
<!-- /changes -->

- [`.claude/skills/write-specs/scripts/specs.py`](../../../.claude/skills/write-specs/scripts/specs.py), [`spec_model.py`](../../../.claude/skills/write-specs/scripts/spec_model.py), [`spec_check.py`](../../../.claude/skills/write-specs/scripts/spec_check.py), [`SKILL.md`](../../../.claude/skills/write-specs/SKILL.md), [`.claude/rules/specs.md`](../../../.claude/rules/specs.md) and [`.claude/rules/enforcement.json`](../../../.claude/rules/enforcement.json): the build writes and the check compares the tokens file (SPEC-11, SPEC-13), with the rule and its enforcers updated.
- [`packages/ts/tokens/`](../../../packages/ts/tokens/package.json): the generated tokens package.
- [`packages/ts/ui/src/layout`](../../../packages/ts/ui/src/layout/layout.css), [`controls`](../../../packages/ts/ui/src/controls/controls.css), [`overlays`](../../../packages/ts/ui/src/overlays/overlays.css), [`feedback`](../../../packages/ts/ui/src/feedback/feedback.css), [`data`](../../../packages/ts/ui/src/data/data.css): the components of the component sheet, one folder and one stylesheet per group.
- [`packages/ts/ui/src/frames/`](../../../packages/ts/ui/src/frames/frames.css): the building blocks (lines 1-32 of each file are small) and the five frames, with [`parts.ts`](../../../packages/ts/ui/src/frames/parts.ts) holding the words.
- [`packages/ts/ui/test/`](../../../packages/ts/ui/test/frames.test.tsx): tests for every group, the styles and the frames.
- [`frontends/ground-control`](../../../frontends/ground-control/package.json), [`mission-studio`](../../../frontends/mission-studio/package.json), [`back-office`](../../../frontends/back-office/package.json), [`client-portal`](../../../frontends/client-portal/package.json): the four shells, each with its Vite and TypeScript set-up and a test that it renders its frame.
- [`frontends/desktop/`](../../../frontends/desktop/package.json): the Tauri 2 shell, its assembler, Rust crate, capability and icons.
- [`.github/workflows/desktop.yml`](../../../.github/workflows/desktop.yml) and [`.github/workflows/automerge.yml`](../../../.github/workflows/automerge.yml): the three-system build, and the automerge wait for it.
- [`tests/harness/write_specs/test_tokens_package.py`](../../../tests/harness/write_specs/test_tokens_package.py), [`tests/ci/workflows/test_desktop_workflow.py`](../../../tests/ci/workflows/test_desktop_workflow.py), [`tests/conventions/mono_repo/test_desktop_shell.py`](../../../tests/conventions/mono_repo/test_desktop_shell.py), [`tests/conventions/mono_repo/test_frontend_workspace.py`](../../../tests/conventions/mono_repo/test_frontend_workspace.py): the Python tests of the pipeline and of the layout.
- [`AGENT.md`](../../../AGENT.md), [`README.md`](../../../README.md), [`.gitignore`](../../../.gitignore), [`pnpm-lock.yaml`](../../../pnpm-lock.yaml): the front-end commands and layout, and the lock. These shared files also hold other tickets' text (see the follow-ups).

## 🧪 How to test it

```bash
python3 .claude/skills/write-specs/scripts/specs.py check
uv run pytest tests/harness/write_specs/test_tokens_package.py -n 2
pnpm install --frozen-lockfile
pnpm -r --if-present lint
pnpm -r --if-present typecheck
pnpm -r --if-present test
uv run pytest tests/ci/workflows/test_desktop_workflow.py tests/conventions/mono_repo -n 2
```

The first command shows the tokens file is current. The second changes a token and checks the package follows. The pnpm commands lint, type-check and test the UI package and the four shells. The last runs the desktop and layout tests. The real three-system build runs in the `desktop` CI job.

## 🔗 Evidence

- [Specs check](tests-evidences/specs-check.txt): empty, so every page and the generated files are current.
- [Python tests](tests-evidences/pytest.txt): 2436 passed.
- [Ruff check](tests-evidences/ruff-check.txt) and [ruff format](tests-evidences/ruff-format.txt), [mypy](tests-evidences/mypy.txt): Python checks.
- [pnpm install](tests-evidences/pnpm-install.txt): the frozen install passes on 10 projects.
- [Lint](tests-evidences/lint.txt), [typecheck](tests-evidences/typecheck.txt) and [test](tests-evidences/test.txt): UI package 154 tests, back-office 8, mission-studio 8, ground-control 10, client-portal 9.
- [Ticket references](tests-evidences/ticket-refs.txt) and [plan view](tests-evidences/plan-view.txt): the ticket and plan documents are consistent.

## 📝 Assumptions accepted

- The roadmap row names no feature or use case, so the ticket links none. BR-017 is linked only because the epic row names it. Accepted: language support belongs to T0.15.
- The ticket link points to the sprint anchor `#s03` because the roadmap row has no anchor of its own. Accepted: it is the closest anchor that resolves.
- `➖ No screen`: the four shells are empty frames and show no use case state. Accepted: the UC-029 screenshots are in T0.20's scope.

## 🔜 Follow-ups

| File | What to change |
| --- | --- |
| [`AGENT.md:252-399`](../../../AGENT.md#L252-L399) | T0.10, T0.11, T0.12, T0.13 and T0.15 also claim AGENT.md (and README.md, pnpm-lock.yaml, automerge.yml). This diff holds their text too: `images.yml`, cosign, swarm-storage, swarm-rest, the simulator and the PostgreSQL fixtures. If T0.14 runs `finish` first, develop gets documentation for code that is not there yet. Let those tickets finish first, or give the harness ownership of hunks in shared files. The extra `packages/ts/e2e` importer in the lock does no harm: the frozen install passes without it ([evidence](tests-evidences/pnpm-install.txt)). Owner: the harness (`ticket_tree.py`) |
| [`tests/conventions/mono_repo/test_frontend_workspace.py`](../../../tests/conventions/mono_repo/test_frontend_workspace.py) | `tests/conventions/mono_repo/` holds 7 Python files and `tests/ci/workflows/` holds 7. Split them into sub-folders, for example `mono_repo/frontends/`. Owners: K02, K03 |
| [`tests/harness/write_specs/test_tokens_package.py:21-38`](../../../tests/harness/write_specs/test_tokens_package.py#L21-L38) | Move the module-level constants to [`helpers.py`](../../../tests/harness/write_specs/helpers.py), or make them `ClassVar`s of `TestTokensPackage`. Move the `root` and `built` fixtures to a fixtures file. Owner: K01 |
| [`packages/ts/ui/src/frames/GroundControlFrame.tsx`](../../../packages/ts/ui/src/frames/GroundControlFrame.tsx) | The Mission state is plain text, not the badge the Frames table asks for (assumption K16). Once a Mission state is shown on a screen (T0.19), choose its Badge kind in the visual identity and render a Badge. The same applies to `MissionStudioFrame`. Owner: K16 |
| [`frontends/desktop/src-tauri/tauri.conf.json:28`](../../../frontends/desktop/src-tauri/tauri.conf.json#L28) | `style-src 'self'` blocks `<style>` elements added at run time, such as the scroll-lock style of Radix Dialog. Styles set through React's `style` prop are not affected. When the desktop first shows a Dialog, check the console. If blocked, add the narrow `style-src-elem` exception with a nonce, or `'unsafe-inline'` limited to style elements. Owner: K21 |
| [`frontends/ground-control/src/main.tsx:9`](../../../frontends/ground-control/src/main.tsx#L9) | Two apps find the root with `querySelector('#root')` and two with `getElementById('root')`. Ground control also uses single quotes where the others use double. Pick one form for all four. Owners: K17 to K20 |
| [`AGENT.md:312-317`](../../../AGENT.md#L312-L317) | Rewrap the lines that run past 120 characters: the Mono-repo test paragraph, the front-end packages paragraph, and line 345 of [`.claude/rules/specs.md`](../../../.claude/rules/specs.md). Owner: K22, and K15 for specs.md |
| [`frontends/ground-control`](../../../frontends/ground-control/package.json) | The four apps have no Dockerfile and no `e2e/` folder yet, which the plan left to T0.10 and T0.20. Check that T0.20 covers the light and dark Playwright run of the four shells, the real browser evidence for criterion 2 |
| [`pnpm-lock.yaml:196`](../../../pnpm-lock.yaml#L196) | The lock changed again in the fix round. Besides the `supports-color` peer re-resolution, it holds the `packages/ts/api-client` importer and the `openapi-fetch`, `openapi-typescript` and `@redocly/*` entries from T0.12's uncommitted work. T0.10 and T0.12 also own the file. The frozen install passes on T0.14's own files, but its commit would carry T0.12's entries. Decide at `finish` which ticket commits the lock, or regenerate it on T0.14's own tree. Owner: K11 (integrator) |
| [`tests/ci/workflows/test_desktop_workflow.py`](../../../tests/ci/workflows/test_desktop_workflow.py) | Add a test that the Linux step of [`desktop.yml`](../../../.github/workflows/desktop.yml) does not install `libappindicator3-dev`, so the package cannot come back. Owner: K11 |
