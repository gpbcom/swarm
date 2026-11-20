from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from spec_model import (CLASSDEF, DOC_CLASSES, KIND_LABELS, KINDS, MERMAID, ORDER, Page, h2s, links, palette,
                        relpath, set_block, strip_blocks)


def references(pages: List[Page]) -> Dict[Path, List[Page]]:
    by_path = {p.path: p for p in pages}
    graph: Dict[Path, List[Page]] = {}
    for page in pages:
        if page.kind not in ("FS", "UC"):
            continue
        targets = {link.path for link in links(page, strip_blocks(page.text)) if link.path in by_path}
        graph[page.path] = sorted((by_path[t] for t in targets if t and by_path[t].kind in KINDS and t != page.path),
                                  key=lambda p: (ORDER.index(p.kind), p.path.name))
    return graph


def nav(pages: List[Page], index: int, bottom: bool) -> str:
    page = pages[index]
    parts: List[str] = []
    if index > 0:
        previous = pages[index - 1]
        parts.append(f"[🏠 Index]({relpath(page.path, pages[0].path)})")
        parts.append(f"[◀️ {previous.title}]({relpath(page.path, previous.path)})")
    parts.append(f"📄 **Page {index + 1} / {len(pages)}**")
    if index + 1 < len(pages):
        following = pages[index + 1]
        parts.append(f"[{following.title} ▶️]({relpath(page.path, following.path)})")
    line = "> " + " · ".join(parts)
    return f"---\n\n{line}" if bottom else line


def summary(text: str) -> str:
    entries = [f"{n}. [{title}](#{anchor})" for n, (anchor, title) in enumerate([h for h in h2s(text) if h[0]], 1)]
    return '## <a id="summary"></a>📑 Summary\n\n' + "\n".join(entries)


def pages_table(pages: List[Page], index_page: Page) -> str:
    rows = ["| # | Page | Kind | Status |", "| ---: | --- | --- | --- |"]
    for number, page in enumerate(pages, 1):
        rows.append(f"| {number} | [{page.heading}]({relpath(index_page.path, page.path)}) | "
                    f"{KIND_LABELS[page.kind]} | {page.status} |")
    return "\n".join(rows)


def matrix(pages: List[Page], graph: Dict[Path, List[Page]], functional: Page, styles: Dict[str, str]) -> str:
    features = [p for p in pages if p.kind == "FS"]
    if not features:
        return '> [!NOTE]\n> No feature yet. Create one with `specs.py new fs "Title"`.'

    def cell(targets: List[Page]) -> str:
        return "<br>".join(f"[{t.heading}]({relpath(functional.path, t.path)})" for t in targets) or "❌ None"

    rows = ["| 📘 Feature | 🎬 Use cases | 📏 Business rules |", "| --- | --- | --- |"]
    for feature in features:
        targets = graph.get(feature.path, [])
        rows.append(f"| [{feature.heading}]({relpath(functional.path, feature.path)}) | "
                    f"{cell([t for t in targets if t.kind == 'UC'])} | {cell([t for t in targets if t.kind == 'BR'])} |")
    chart: List[str] = ["```mermaid", "flowchart LR"]
    for page in (p for p in pages if p.kind in KINDS):
        chart.append(f'    {page.ident.replace("-", "")}["{KINDS[page.kind][1]} {page.ident}"]:::{DOC_CLASSES[page.kind]}')
    for source in (p for p in pages if p.kind in ("FS", "UC")):
        for target in graph.get(source.path, []):
            chart.append(f"    {source.ident.replace('-', '')} --> {target.ident.replace('-', '')}")
    chart += [f"    classDef {name} {styles[name]}" for name in DOC_CLASSES.values()]
    chart.append("```")
    return "\n".join(rows) + "\n\n" + "\n".join(chart)


def backlinks(pages: List[Page], graph: Dict[Path, List[Page]], page: Page) -> str:
    sources = [p for p in pages if any(t.path == page.path for t in graph.get(p.path, []))]
    if not sources:
        return "> [!WARNING]\n> No feature refers to this page yet."
    return "\n".join(f"- [{s.heading}]({relpath(page.path, s.path)})" for s in sources)


def palette_block(styles: Dict[str, str]) -> str:
    definitions = [f"classDef {name} {style}" for name, style in styles.items()]
    sample = [
        "```mermaid",
        "flowchart LR",
        '    P(["👤 Persona"]):::persona -- "acts" --> A["Action"]:::action',
        '    S[["⚙️ System"]]:::system -- "answers" --> A',
        '    A -- "reads or writes" --> E[("🗃️ Entity")]:::entity',
        '    A --> D{"❓ Decision"}:::decision',
        '    D -- "yes" --> OK(["✅ Success"]):::success',
        '    D -- "no" --> KO(["❌ Failure"]):::failure',
        '    F["📘 Feature"]:::feature --> U["🎬 Use case"]:::usecase --> R["📏 Business rule"]:::rule',
    ] + [f"    {line}" for line in definitions] + ["```"]
    return "```text\n" + "\n".join(definitions) + "\n```\n\n" + "\n".join(sample)


def normalise_classdefs(text: str, styles: Dict[str, str]) -> str:
    def fix_chart(match: re.Match[str]) -> str:
        return CLASSDEF.sub(lambda m: m.group(0).replace(m.group(2), styles[m.group(1)], 1)
                            if m.group(1) in styles else m.group(0), match.group(0))

    return MERMAID.sub(fix_chart, text)


def build_texts(pages: List[Page], tokens: Dict[str, str]) -> Dict[Path, str]:
    graph = references(pages)
    styles = palette(tokens)
    built: Dict[Path, str] = {}
    for number, page in enumerate(pages):
        text = normalise_classdefs(page.text, styles)
        text = set_block(text, "nav-top", nav(pages, number, False))
        text = set_block(text, "nav-bottom", nav(pages, number, True))
        if page.kind == "index":
            text = set_block(text, "pages", pages_table(pages, page))
        if page.kind == "identity":
            text = set_block(text, "palette", palette_block(styles))
        if page.kind == "functional":
            text = set_block(text, "matrix", matrix(pages, graph, page, styles))
        if page.kind in ("UC", "BR"):
            text = set_block(text, "referenced-by", backlinks(pages, graph, page))
        built[page.path] = set_block(text, "summary", summary(text))
    return built
