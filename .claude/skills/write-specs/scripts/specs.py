#!/usr/bin/env python3
from __future__ import annotations

import datetime
import sys
from pathlib import Path
from typing import List

from spec_build import build_texts
from spec_check import Checker
from spec_model import (FIXED_FILES, FIXED_PAGES, IDENTITY_CSS, IDENTITY_GROUP, ID_FILE, KINDS, MODES, MOCKUPS,
                        ROOT, SPECS, TEMPLATES, discover, flowchart, identity_css, nodes, parse_tokens, screen_size,
                        slugify)
from spec_screens import SOURCE_KEY, find_browser, mockups, png_for, png_info, render, source_hash

USAGE = """Build and check the specifications under ``docs/specs`` against the SPEC rules (``.claude/rules/specs.md``).

Usage, from anywhere:
    python3 .claude/skills/write-specs/scripts/specs.py init
    python3 .claude/skills/write-specs/scripts/specs.py new fs|uc|br "Title"
    python3 .claude/skills/write-specs/scripts/specs.py mockup UC-001 A1
    python3 .claude/skills/write-specs/scripts/specs.py render [--all] [UC-001 ...]
    python3 .claude/skills/write-specs/scripts/specs.py build
    python3 .claude/skills/write-specs/scripts/specs.py check

``init``    creates the fixed pages, components.css and the component sheet when missing or empty, then renders.
``new``     creates the next feature (FS), use case (UC) or business rule (BR) from its template, then builds.
``mockup``  creates the HTML mock-up of one state (a flow chart node) of a use case, to draw with components.css.
``render``  builds, then renders every mock-up whose PNG is missing or out of date (all of them with --all).
``build``   rewrites the generated content: summaries, navigation, page list, matrix, back links, palette, the
            flow chart colours and visual-identity.css. It never touches other text.
``check``   prints one line per breach, ``<file>: SPEC-<n>: <message>``, and exits 1. It prints nothing and exits 0
            when the specifications comply.
"""


def today() -> str:
    return datetime.date.today().isoformat()


def show(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def command_init() -> int:
    targets = {SPECS / rel: template for rel, _, template in FIXED_PAGES.values()}
    targets.update(FIXED_FILES)
    for path, template in targets.items():
        if not path.exists() or not path.read_text(encoding="utf-8").strip():
            path.parent.mkdir(parents=True, exist_ok=True)
            text = (TEMPLATES / template).read_text(encoding="utf-8").replace("%DATE%", today())
            path.write_text(text, encoding="utf-8")
            print(f"created {show(path)}")
    return command_render([])


def command_new(kind_arg: str, title: str) -> int:
    kind = kind_arg.upper()
    if kind not in KINDS or not title.strip():
        print('usage: specs.py new fs|uc|br "Title"', file=sys.stderr)
        return 2
    folder, _, template = KINDS[kind]
    directory = SPECS / folder
    directory.mkdir(parents=True, exist_ok=True)
    numbers = [int(m.group(2)) for f in directory.glob("*.md") if (m := ID_FILE.match(f.name))]
    ident = f"{kind}-{max(numbers, default=0) + 1:03d}"
    path = directory / f"{ident}-{slugify(title)}.md"
    text = (TEMPLATES / template).read_text(encoding="utf-8")
    text = text.replace("%ID%", ident).replace("%TITLE%", title.strip()).replace("%DATE%", today())
    path.write_text(text, encoding="utf-8")
    print(f"created {show(path)}")
    return command_build()


def command_mockup(group: str, node_id: str) -> int:
    pages, _ = discover()
    title = node_id
    if group != IDENTITY_GROUP:
        page = next((p for p in pages if p.kind == "UC" and p.ident == group), None)
        if page is None:
            print(f"no use case {group}.", file=sys.stderr)
            return 2
        chart = flowchart(page.text)
        node = next((n for n in nodes(chart or "") if n.ident.lower() == node_id.lower()), None)
        if node is None:
            print(f"{group} has no flow chart node {node_id}.", file=sys.stderr)
            return 2
        title = f"{node.ident}: {node.name}"
    path = MOCKUPS / group / f"{node_id.lower()}.html"
    if path.exists():
        print(f"{show(path)} already exists.", file=sys.stderr)
        return 2
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (TEMPLATES / "mockup.html").read_text(encoding="utf-8")
    path.write_text(text.replace("%GROUP%", group).replace("%TITLE%", title), encoding="utf-8")
    print(f"created {show(path)}: draw the screen, then run specs.py render {group}")
    return 0


def command_render(args: List[str]) -> int:
    command_build()
    force = "--all" in args
    groups = {a for a in args if a != "--all"}
    pages, _ = discover()
    size = screen_size(parse_tokens(pages))
    browser = find_browser()
    if size is None or browser is None:
        print("cannot render: " + ("the visual identity sets no screen.width and screen.height."
                                   if size is None else "no Chrome or Chromium found, set SPECS_BROWSER."),
              file=sys.stderr)
        return 1
    failures = 0
    for html in mockups():
        if groups and html.parent.name not in groups:
            continue
        for mode in MODES:
            png = png_for(html, mode)
            if not force and png.is_file() and png_info(png)[1].get(SOURCE_KEY) == source_hash(html, mode):
                continue
            problem = render(browser, html, size, mode)
            print(f"{'FAILED' if problem else 'rendered'} {show(png)}{': ' + problem if problem else ''}")
            failures += bool(problem)
    return 1 if failures else 0


def command_build() -> int:
    pages, _ = discover()
    tokens = parse_tokens(pages)
    for path, text in build_texts(pages, tokens).items():
        if text != path.read_text(encoding="utf-8"):
            path.write_text(text, encoding="utf-8")
    if tokens:
        css = identity_css(tokens, parse_tokens(pages, "dark"))
        if not IDENTITY_CSS.is_file() or IDENTITY_CSS.read_text(encoding="utf-8") != css:
            IDENTITY_CSS.parent.mkdir(parents=True, exist_ok=True)
            IDENTITY_CSS.write_text(css, encoding="utf-8")
    return 0


def command_check() -> int:
    errors = Checker(*discover()).run()
    for line in errors:
        print(line)
    return 1 if errors else 0


def main() -> int:
    match sys.argv[1:]:
        case ["init"]:
            return command_init()
        case ["new", kind, *words]:
            return command_new(kind, " ".join(words))
        case ["mockup", group, node_id]:
            return command_mockup(group, node_id)
        case ["render", *args]:
            return command_render(args)
        case ["build"]:
            return command_build()
        case ["check"]:
            return command_check()
        case _:
            print(USAGE, file=sys.stderr)
            return 2


if __name__ == "__main__":
    sys.exit(main())
