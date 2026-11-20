from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Set

from spec_build import build_texts, references
from spec_model import (ANCHOR, ARROW, CLASSDEF, COMMON_BLOCKS, COMPONENTS_CSS, DEFAULT_COLOURS, EXTRA_BLOCKS,
                        FIXED_PAGES, GLOSSARY_CLASSES, H1, IDENTITY_CSS, TOKENS_CSS, IDENTITY_GROUP, ID_FILE, KINDS, MODES, MOCKUPS,
                        REQUIRED_SECTIONS, REQUIRED_TOKENS, ROOT, RULE_TYPE, SCREEN_CLASSES, SCREEN_SOURCES, SCREENS,
                        SPECS, STATUS_KINDS, STATUSES, RULE_TYPES, Node, Page, Term, dark_tokens, flowchart, h2s,
                        has_block, identity_css, images, links, nodes, palette, parse_glossary, parse_tokens, relpath,
                        screen_size, section, strip_blocks, strip_fences, strip_icon)
from spec_screens import (PALETTE_TYPE, SOURCE_KEY, mockup_for, mockups, mode_of, png_colour_type, png_for, png_info,
                          screen_pngs, source_hash)

SCREEN_ROW = re.compile(r'^\|\s*<a id="screen-([a-z0-9_-]+)"></a>')
SCREEN_IMAGE = re.compile(r"^\[!\[([^\]]+)\]\(([^)\s]+)\)\]\(([^)\s]+)\)\s*(?:<br>)?\s*"
                          r"\[!\[([^\]]+)\]\(([^)\s]+)\)\]\(([^)\s]+)\)$")
RAW_COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\(")
RAW_FONT = re.compile(r"\bfont(?:-family|-size)?\s*:(?!\s*var\()", re.I)
STYLESHEET = re.compile(r"<link\b[^>]*\bhref=\"([^\"]+\.css)\"", re.I)


class Checker:
    def __init__(self, pages: List[Page], unknown: List[Path]) -> None:
        self.pages = pages
        self.unknown = unknown
        self.by_path = {p.path: p for p in pages}
        self.graph = references(pages)
        self.errors: List[str] = []
        self.glossary = next((p for p in pages if p.kind == "glossary"), None)
        self.identity = next((p for p in pages if p.kind == "identity"), None)
        self.terms: Dict[str, Term] = {}
        self.names: Dict[str, Term] = {}
        self.tokens = parse_tokens(pages)
        self.dark = parse_tokens(pages, "dark")
        self.with_dark = dark_tokens(pages)
        self.styles = palette(self.tokens)
        self.states_shown: Set[str] = set()

    def error(self, path: Path, rule: int, message: str) -> None:
        self.errors.append(f"{path.relative_to(ROOT).as_posix()}: SPEC-{rule}: {message}")

    def run(self) -> List[str]:
        for path in self.unknown:
            self.error(path, 1, "page outside the layout: move it under functional/ or technical/, or delete it.")
        present = {p.kind for p in self.pages}
        for kind, (rel, _, _) in FIXED_PAGES.items():
            if kind not in present:
                self.error(SPECS / rel, 1, "missing page: run specs.py init.")
        self.check_glossary()
        self.check_identity()
        self.check_ids()
        built = build_texts(self.pages, self.tokens)
        for page in self.pages:
            self.check_page(page)
            if built[page.path] != page.text:
                self.error(page.path, 11, "generated content is out of date: run specs.py build.")
        self.check_states_shown()
        self.check_screen_files()
        return self.errors

    # Glossary and visual identity ------------------------------------------------------------------------------

    def check_glossary(self) -> None:
        if not self.glossary:
            return
        self.terms, problems = parse_glossary(self.glossary.text)
        for problem in problems:
            self.error(self.glossary.path, 2, problem)
        self.names = {t.name.lower(): t for t in self.terms.values()}
        for term in (t for t in self.terms.values() if t.kind == "state"):
            owner = self.names.get(term.owner.lower())
            if ":" not in term.name or not owner or owner.kind not in ("persona", "entity"):
                self.error(self.glossary.path, 2, f"state '{term.name}' must read '<persona or entity>: <state>' "
                                                  "with a persona or an entity of the glossary.")

    def check_identity(self) -> None:
        if not self.identity:
            return
        for name in REQUIRED_TOKENS:
            if name not in self.tokens:
                self.error(self.identity.path, 13, f"token `{name}` is missing.")
        for name, value in self.tokens.items():
            if name.startswith("color.") and not re.fullmatch(r"#[0-9a-f]{6}", value):
                self.error(self.identity.path, 13, f"token `{name}` must be a lower-case #rrggbb colour, not {value}.")
            if name.startswith(("screen.", "space.", "radius.", "size.")) and not re.fullmatch(r"\d+px", value):
                self.error(self.identity.path, 13, f"token `{name}` must be a size in px, not {value}.")
        for name in (n for n in self.tokens if n.startswith("color.") and n not in self.with_dark):
            self.error(self.identity.path, 13, f"token `{name}` has no dark mode value (third column).")
        for name, value in self.dark.items():
            if name.startswith("color.") and name in self.with_dark and not re.fullmatch(r"#[0-9a-f]{6}", value):
                self.error(self.identity.path, 13, f"dark value of `{name}` must be a lower-case #rrggbb colour.")
        expected = identity_css(self.tokens, self.dark)
        if not IDENTITY_CSS.is_file() or IDENTITY_CSS.read_text(encoding="utf-8") != expected:
            self.error(IDENTITY_CSS, 11, "out of date: run specs.py build.")
        if not TOKENS_CSS.is_file() or TOKENS_CSS.read_text(encoding="utf-8") != expected:
            self.error(TOKENS_CSS, 11, "out of date: run specs.py build.")

    def check_ids(self) -> None:
        seen: Dict[str, Page] = {}
        for page in (p for p in self.pages if p.kind in KINDS):
            match = ID_FILE.match(page.path.name)
            if not match or match.group(1) != page.kind:
                self.error(page.path, 1, f"file name must be {page.kind}-<3 digits>-<kebab-case-slug>.md.")
                continue
            if page.ident in seen:
                self.error(page.path, 1, f"{page.ident} is already used by {seen[page.ident].rel}.")
            seen[page.ident] = page

    # Pages -----------------------------------------------------------------------------------------------------

    def check_page(self, page: Page) -> None:
        self.check_headings(page)
        self.check_blocks(page)
        self.check_writing(page.path, page.text)
        self.check_links(page)
        if page.kind != "glossary":
            self.check_aliases(page.path, self.prose(page.text))
        if page.kind in STATUS_KINDS:
            self.check_status(page)
        if page.kind == "FS":
            self.check_feature(page)
        if page.kind == "UC":
            self.check_use_case(page)
        if page.kind in ("UC", "BR"):
            self.check_orphan(page)

    def check_headings(self, page: Page) -> None:
        titles = H1.findall(strip_fences(page.text))
        if len(titles) != 1:
            self.error(page.path, 1, f"a page has exactly one '# ' title, found {len(titles)}.")
        icon = FIXED_PAGES[page.kind][1] if page.kind in FIXED_PAGES else KINDS.get(page.kind, ("", "", ""))[1]
        if icon and not page.heading.startswith(icon + " "):
            self.error(page.path, 8, f"the title must start with the icon {icon}.")
        if not icon and not re.match(r"[^\w\s]", page.heading):
            self.error(page.path, 8, "the title must start with an icon.")
        if page.kind in KINDS and page.ident and not re.match(rf"^{KINDS[page.kind][1]} {page.ident}: \S", page.heading):
            self.error(page.path, 1, f"the title must read '# {KINDS[page.kind][1]} {page.ident}: <Title>'.")
        anchors: List[str] = []
        for anchor, title in h2s(page.text):
            if anchor is None:
                self.error(page.path, 5, f"heading '## {title}' needs an anchor: '## <a id=\"slug\"></a><icon> {title}'.")
                continue
            anchors.append(anchor)
            if not re.match(r"[^\w\s\[*`]", title):
                self.error(page.path, 8, f"heading '{title}' must start with an icon.")
        required = REQUIRED_SECTIONS[page.kind]
        for anchor in required:
            if anchor not in anchors:
                self.error(page.path, 5, f"required section '{anchor}' is missing.")
        positions = [anchors.index(a) for a in required if a in anchors]
        if positions != sorted(positions):
            self.error(page.path, 5, f"sections must come in this order: {', '.join(required)}.")
        ids = ANCHOR.findall(strip_blocks(page.text, {"summary"}))
        for duplicate in sorted({i for i in ids if ids.count(i) > 1}):
            self.error(page.path, 9, f"anchor '{duplicate}' is defined twice.")

    def check_blocks(self, page: Page) -> None:
        for name in COMMON_BLOCKS + EXTRA_BLOCKS.get(page.kind, []):
            if not has_block(page.text, name):
                rule = {"summary": 6, "pages": 6, "nav-top": 7, "nav-bottom": 7, "palette": 13}.get(name, 3)
                self.error(page.path, rule, f"generated block '{name}' is missing: add its two markers "
                                            f"'<!-- spec:{name} -->' and '<!-- /spec:{name} -->'.")

    def check_writing(self, path: Path, text: str) -> None:
        if "—" in text:
            self.error(path, 10, "em dash found: use a colon, a comma or two sentences.")
        for placeholder in sorted(set(re.findall(r"\{\{[^}]*\}\}", text)))[:5]:
            self.error(path, 10, f"placeholder left: {placeholder}")

    def check_status(self, page: Page) -> None:
        if page.status not in STATUSES:
            self.error(page.path, 8, f"status line '**Status:** <status>' must use one of: {', '.join(STATUSES)}.")
        if page.kind == "BR":
            match = RULE_TYPE.search(page.text)
            if not match or match.group(1).strip() not in RULE_TYPES:
                self.error(page.path, 5, f"'**Type:**' must be one of: {', '.join(RULE_TYPES)}.")

    def check_links(self, page: Page) -> None:
        for image in images(page):
            if image.path is not None and not image.path.is_file():
                self.error(page.path, 9, f"missing image: ![{image.text}]({image.target})")
        for link in links(page):
            if link.path is None:
                continue
            if not link.path.is_file():
                self.error(page.path, 9, f"broken link: [{link.text}]({link.target})")
                continue
            if link.fragment:
                target_text = self.by_path[link.path].text if link.path in self.by_path else \
                    link.path.read_text(encoding="utf-8", errors="replace")
                if link.fragment not in ANCHOR.findall(target_text):
                    self.error(page.path, 9, f"anchor not found: [{link.text}]({link.target})")
            target = self.by_path.get(link.path)
            if target and target is not page and target.kind in KINDS and target.ident not in link.text:
                self.error(page.path, 3, f"link to {target.ident} must show its ID: [{link.text}]({link.target})")
            if self.glossary and link.path == self.glossary.path and link.fragment in self.terms:
                term = self.terms[link.fragment]
                label = strip_icon(link.text).lower()
                if label not in (term.name.lower(), term.name.lower() + "s", term.name.lower() + "es"):
                    self.error(page.path, 2, f"link to the glossary row '{term.name}' reads '{strip_icon(link.text)}'.")

    def prose(self, text: str) -> str:
        prose = strip_blocks(text)
        prose = re.sub(r"<!--.*?-->", " ", prose, flags=re.S)
        prose = re.sub(r"\]\([^)]*\)", "]", prose)
        return re.sub(r"<[^>]+>|`[^`\n]*`", " ", prose)

    def check_aliases(self, path: Path, prose: str) -> None:
        if not self.terms:
            return
        for name in sorted((t.name for t in self.terms.values()), key=len, reverse=True):
            prose = re.sub(rf"(?i)\b{re.escape(name)}\b", " ", prose)
        for term in self.terms.values():
            for alias in term.aliases:
                if re.search(rf"(?i)\b{re.escape(alias)}(s|es)?\b", prose):
                    self.error(path, 2, f"'{alias}' is not a glossary name: write '{term.name}'.")

    def check_feature(self, page: Page) -> None:
        for anchor, kind, label in (("business-rules", "BR", "business rule"), ("use-cases", "UC", "use case")):
            targets = [self.by_path[link.path] for link in links(page, section(page.text, anchor))
                       if link.path in self.by_path and self.by_path[link.path].kind == kind]
            if not targets:
                self.error(page.path, 3, f"section '{anchor}' must link to at least one existing {label} ({kind}).")

    def check_orphan(self, page: Page) -> None:
        if not any(any(t.path == page.path for t in targets) for source, targets in self.graph.items()
                   if self.by_path[source].kind == "FS"):
            self.error(page.path, 3, f"no feature (FS) refers to {page.ident or page.rel}.")

    # Use cases: flow chart and screens --------------------------------------------------------------------------

    def glossary_fragments(self, page: Page, text: str) -> List[str]:
        return [link.fragment for link in links(page, text)
                if self.glossary and link.path == self.glossary.path and link.fragment in self.terms]

    def check_use_case(self, page: Page) -> None:
        chart = flowchart(page.text)
        if chart is None:
            self.error(page.path, 4, "section 'flowchart' must hold a ```mermaid flowchart, written in the page.")
            return
        chart_nodes = nodes(chart)
        definitions = dict(CLASSDEF.findall(chart))
        for name, style in definitions.items():
            if name in self.styles and style.strip() != self.styles[name]:
                self.error(page.path, 8, f"classDef {name} must be: {self.styles[name]}")
        for cls in sorted({n.cls for n in chart_nodes}):
            if cls not in DEFAULT_COLOURS or cls in ("feature", "usecase", "rule"):
                self.error(page.path, 8, f"class '{cls}' is not a flow chart class of the visual identity.")
            elif cls not in definitions:
                self.error(page.path, 8, f"classDef {cls} is missing: {self.styles[cls]}")
        for required in ("persona", "entity"):
            if not any(n.cls == required for n in chart_nodes):
                self.error(page.path, 4, f"the flow chart needs at least one :::{required} node.")
        actors = {f for f in self.glossary_fragments(page, section(page.text, "actors"))
                  if self.terms[f].kind in GLOSSARY_CLASSES}
        arrows = [line for line in chart.splitlines() if ARROW.search(line) and "classDef" not in line]
        charted: Set[str] = set()
        for node in (n for n in chart_nodes if n.cls in GLOSSARY_CLASSES):
            term = self.names.get(node.name.lower())
            if not term or term.kind != node.cls:
                self.error(page.path, 2, f"'{node.name}' is not a {node.cls} of the glossary.")
            else:
                charted.add(term.anchor)
                if term.anchor not in actors:
                    self.error(page.path, 4, f"section 'actors' must link to the glossary row of '{term.name}'.")
            if not any(re.search(rf"\b{re.escape(node.ident)}\b", line) for line in arrows):
                self.error(page.path, 4, f"node '{node.name}' takes part in no interaction (no arrow).")
        for anchor in sorted(actors - charted):
            self.error(page.path, 4, f"'{self.terms[anchor].name}' is listed in section 'actors' but is missing "
                                     "from the flow chart.")
        self.check_screen_rows(page, chart_nodes)

    def check_screen_rows(self, page: Page, chart_nodes: List[Node]) -> None:
        rows: Dict[str, List[str]] = {}
        for line in section(page.text, "screens").splitlines():
            match = SCREEN_ROW.match(line)
            if not match:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) != 5:
                self.error(page.path, 12, f"screen row '{match.group(1)}' needs 5 cells: state, persona, entity, "
                                          "source, screen.")
                continue
            rows[match.group(1)] = cells
        by_id = {n.ident.lower(): n for n in chart_nodes}
        actor_names = {n.name.lower() for n in chart_nodes if n.cls in GLOSSARY_CLASSES}
        for node in (n for n in chart_nodes if n.cls in SCREEN_CLASSES):
            if node.ident.lower() not in rows:
                self.error(page.path, 12, f"state '{node.ident}: {node.name}' of the flow chart has no row in "
                                          f"section 'screens' (anchor screen-{node.ident.lower()}).")
        for row_id, (_, persona, entity, source, screen) in rows.items():
            node = by_id.get(row_id)
            if not node or node.cls in GLOSSARY_CLASSES:
                self.error(page.path, 12, f"screen row '{row_id}' matches no state node of the flow chart.")
            named = 0
            for cell, kind in ((persona, "persona"), (entity, "entity")):
                fragments = self.glossary_fragments(page, cell)
                named += len(fragments)
                if not fragments and cell != "➖":
                    self.error(page.path, 12, f"screen row '{row_id}': the {kind} cell links to the glossary or is ➖.")
                for fragment in fragments:
                    term = self.terms[fragment]
                    owner = self.names.get(term.owner.lower()) if term.kind == "state" else term
                    if not owner or owner.kind != kind:
                        self.error(page.path, 12, f"screen row '{row_id}': '{term.name}' is not a {kind} or one "
                                                  f"of its states.")
                    elif owner.name.lower() not in actor_names:
                        self.error(page.path, 12, f"screen row '{row_id}': '{owner.name}' is not in the flow chart.")
                    if term.kind == "state":
                        self.states_shown.add(fragment)
            if not named:
                self.error(page.path, 12, f"screen row '{row_id}' names no persona and no entity.")
            self.check_screen_cell(page, row_id, source, screen)

    def check_screen_cell(self, page: Page, row_id: str, source: str, screen: str) -> None:
        if source not in SCREEN_SOURCES:
            self.error(page.path, 12, f"screen row '{row_id}': source must be one of {', '.join(SCREEN_SOURCES)}.")
            return
        mockup = MOCKUPS / page.ident / f"{row_id}.html"
        if source == "➖":
            if not re.match(r"^➖ No screen: \S.{9,}", screen):
                self.error(page.path, 12, f"screen row '{row_id}': write '➖ No screen: <why nothing is shown>'.")
            return
        light = relpath(page.path, SCREENS / page.ident / f"{row_id}.png")
        dark = relpath(page.path, SCREENS / page.ident / f"{row_id}.dark.png")
        match = SCREEN_IMAGE.match(screen)
        if not match or match.group(2, 3, 5, 6) != (light, light, dark, dark):
            self.error(page.path, 12, f"screen row '{row_id}': the screen cell must show the light then the dark "
                                      f"screen: [![{page.ident} {row_id.upper()}: <state>]({light})]({light}) "
                                      f"[![{page.ident} {row_id.upper()}: <state> (dark)]({dark})]({dark})")
        elif page.ident not in match.group(1) or page.ident not in match.group(4):
            self.error(page.path, 12, f"screen row '{row_id}': the image texts must start with {page.ident}.")
        if source == "✏️ Mock-up" and not mockup.is_file():
            self.error(page.path, 12, f"screen row '{row_id}': mock-up missing, run specs.py mockup "
                                      f"{page.ident} {row_id}.")
        if source == "📸 Screenshot" and mockup.is_file():
            self.error(page.path, 12, f"screen row '{row_id}' is a screenshot: delete its mock-up "
                                      f"{mockup.relative_to(ROOT).as_posix()}.")

    def check_states_shown(self) -> None:
        if not self.glossary:
            return
        for term in (t for t in self.terms.values() if t.kind == "state"):
            if term.anchor not in self.states_shown:
                self.error(self.glossary.path, 12, f"state '{term.name}' has no row in the screens of any use case.")

    # Screen files ----------------------------------------------------------------------------------------------

    def check_screen_files(self) -> None:
        size = screen_size(self.tokens)
        shown = {image.path for page in self.pages for image in images(page)}
        groups = {p.ident for p in self.pages if p.kind == "UC"} | {IDENTITY_GROUP}
        for png in screen_pngs():
            info, texts = png_info(png)
            if png not in shown:
                self.error(png, 12, "screen shown on no page: show it in a use case or delete it.")
            if info is None:
                self.error(png, 12, "not a PNG file.")
            elif png_colour_type(png) != PALETTE_TYPE:
                self.error(png, 13, "not a 256-colour palette PNG: run specs.py render --all, or palettise the screenshot.")
            elif size and tuple(info) != size:
                self.error(png, 13, f"is {info[0]} x {info[1]} px, the visual identity sets {size[0]} x {size[1]} px.")
            mockup = mockup_for(png)
            twin = png.with_name(png.name.replace(".dark.png", ".png")) if mode_of(png) == "dark" else \
                png.with_name(png.stem + ".dark.png")
            if not twin.is_file():
                self.error(png, 13, f"has no {'light' if mode_of(png) == 'dark' else 'dark'} mode twin: {twin.name}.")
            if mockup.is_file() and texts.get(SOURCE_KEY) != source_hash(mockup, mode_of(png)):
                self.error(png, 12, "out of date with its mock-up or the visual identity: run specs.py render.")
        for html in mockups():
            if html.parent.parent != MOCKUPS or html.parent.name not in groups:
                self.error(html, 12, "mock-up outside screens/mockups/<UC-ID or identity>/.")
            for mode in MODES:
                if not png_for(html, mode).is_file():
                    self.error(html, 12, f"not rendered in {mode} mode: run specs.py render.")
            self.check_mockup(html)
        if COMPONENTS_CSS.is_file():
            self.check_css(COMPONENTS_CSS)
        elif self.identity:
            self.error(COMPONENTS_CSS, 13, "missing: run specs.py init.")

    def check_mockup(self, html: Path) -> None:
        text = html.read_text(encoding="utf-8")
        if re.search(r"<style\b|\sstyle\s*=", text, re.I):
            self.error(html, 13, "inline style found: use only the classes of components.css.")
        expected = {relpath(html, IDENTITY_CSS), relpath(html, COMPONENTS_CSS)}
        if set(STYLESHEET.findall(text)) != expected:
            self.error(html, 13, f"must link exactly these stylesheets: {', '.join(sorted(expected))}.")
        self.check_writing(html, text)
        body = re.sub(r"<head\b.*?</head>", " ", text, flags=re.S | re.I)
        self.check_aliases(html, re.sub(r"<!--.*?-->|<[^>]+>", " ", body, flags=re.S))

    def check_css(self, css: Path) -> None:
        for number, line in enumerate(css.read_text(encoding="utf-8").splitlines(), 1):
            if RAW_COLOUR.search(line) or RAW_FONT.search(line):
                self.error(css, 13, f"line {number}: colours and fonts come from the tokens, use var(--...): "
                                    f"{line.strip()}")
