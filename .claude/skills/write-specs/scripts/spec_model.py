from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[4]
SPECS = ROOT / "docs" / "specs"
TEMPLATES = Path(__file__).resolve().parents[1] / "templates"
SCREENS = SPECS / "screens"
MOCKUPS = SCREENS / "mockups"
IDENTITY_CSS = MOCKUPS / "visual-identity.css"
TOKENS_CSS = ROOT / "packages" / "ts" / "tokens" / "src" / "tokens.css"
COMPONENTS_CSS = MOCKUPS / "components.css"
IDENTITY_GROUP = "identity"
MODES = ("light", "dark")

KINDS: Dict[str, Tuple[str, str, str]] = {
    "FS": ("functional/features", "📘", "feature.md"),
    "UC": ("functional/use-cases", "🎬", "use-case.md"),
    "BR": ("functional/business-rules", "📏", "business-rule.md"),
}
FIXED_PAGES: Dict[str, Tuple[str, str, str]] = {
    "index": ("README.md", "🏠", "index.md"),
    "glossary": ("glossary.md", "📖", "glossary.md"),
    "identity": ("visual-identity.md", "🎨", "visual-identity.md"),
    "functional": ("functional/README.md", "🧭", "functional-index.md"),
    "technical": ("technical/README.md", "🛠️", "technical-index.md"),
    "roadmap": ("roadmap/README.md", "🛣️", "roadmap-index.md"),
}
FIXED_FILES: Dict[Path, str] = {
    COMPONENTS_CSS: "components.css",
    MOCKUPS / IDENTITY_GROUP / "components.html": "identity-components.html",
    MOCKUPS / IDENTITY_GROUP / "layouts.html": "identity-layouts.html",
}
ORDER = ["index", "glossary", "identity", "functional", "FS", "UC", "BR", "technical", "technical-page", "roadmap",
         "roadmap-page"]
KIND_LABELS = {
    "index": "Index",
    "glossary": "Glossary",
    "identity": "Visual identity",
    "functional": "Functional overview",
    "FS": "📘 Feature",
    "UC": "🎬 Use case",
    "BR": "📏 Business rule",
    "technical": "Technical overview",
    "technical-page": "🛠️ Technical",
    "roadmap": "Roadmap overview",
    "roadmap-page": "🛣️ Roadmap",
}
REQUIRED_SECTIONS: Dict[str, List[str]] = {
    "index": ["pages", "legend"],
    "glossary": ["personas", "entities", "systems", "terms", "states"],
    "identity": ["principles", "colours", "typography", "spacing", "iconography", "components", "screens",
                 "diagrams"],
    "functional": ["overview", "traceability"],
    "FS": ["goal", "personas", "business-rules", "use-cases", "acceptance", "out-of-scope", "open-questions",
           "references"],
    "UC": ["actors", "preconditions", "trigger", "main-flow", "flowchart", "screens", "alternative-flows",
           "business-rules", "postconditions", "referenced-by"],
    "BR": ["statement", "rationale", "examples", "exceptions", "referenced-by"],
    "technical": ["overview"],
    "technical-page": [],
    "roadmap": ["overview"],
    "roadmap-page": [],
}
COMMON_BLOCKS = ["nav-top", "summary", "nav-bottom"]
EXTRA_BLOCKS: Dict[str, List[str]] = {"index": ["pages"], "functional": ["matrix"], "UC": ["referenced-by"],
                                      "BR": ["referenced-by"], "identity": ["palette"]}
STATUS_KINDS = ("FS", "UC", "BR", "identity")
STATUSES = ("🟡 Draft", "🔵 In review", "🟢 Approved", "🔴 Deprecated")
RULE_TYPES = ("Constraint", "Validation", "Computation", "Authorisation", "Inference")
SCREEN_SOURCES = ("✏️ Mock-up", "📸 Screenshot", "➖")
SCREEN_CLASSES = ("action", "success", "failure")
GLOSSARY_CLASSES = {"persona": "per", "entity": "ent", "system": "sys"}
GLOSSARY_KINDS = {"per": "persona", "ent": "entity", "sys": "system", "term": "term", "st": "state"}
DOC_CLASSES = {"FS": "feature", "UC": "usecase", "BR": "rule"}
BOLD_CLASSES = ("persona", "entity", "system", "feature", "usecase", "rule")
DEFAULT_COLOURS: Dict[str, Tuple[str, str, str]] = {
    "persona": ("#1d4ed8", "#dbeafe", "#0b1f4d"),
    "entity": ("#15803d", "#dcfce7", "#052e16"),
    "system": ("#6d28d9", "#ede9fe", "#2e1065"),
    "action": ("#475569", "#f1f5f9", "#0f172a"),
    "decision": ("#b45309", "#fef3c7", "#451a03"),
    "success": ("#047857", "#d1fae5", "#022c22"),
    "failure": ("#b91c1c", "#fee2e2", "#450a0a"),
    "feature": ("#4338ca", "#e0e7ff", "#1e1b4b"),
    "usecase": ("#0e7490", "#cffafe", "#083344"),
    "rule": ("#c2410c", "#ffedd5", "#431407"),
}
REQUIRED_TOKENS = [
    "color.background", "color.surface", "color.text", "color.muted", "color.border", "color.primary",
    "color.primary-soft", "color.primary-ink", "color.overlay", "font.ui", "font.mono", "font.emoji", "size.title", "size.heading",
    "size.body", "size.small", "space.1", "space.2", "space.3", "space.4", "space.6", "radius.s", "radius.m",
    "shadow.card", "screen.width", "screen.height",
] + [f"color.{cls}{suffix}" for cls in DEFAULT_COLOURS for suffix in ("", "-soft", "-ink")]

LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
H1 = re.compile(r"^# (.+)$", re.M)
H2 = re.compile(r"^## (.*)$", re.M)
H2_ANCHORED = re.compile(r'^<a id="([a-z0-9-]+)"></a>(.*)$')
FENCE = re.compile(r"^```.*?^```[ \t]*$", re.S | re.M)
MERMAID = re.compile(r"^```mermaid[ \t]*\n(.*?)^```", re.S | re.M)
BLOCK_ANY = re.compile(r"<!-- spec:([\w-]+) -->\n.*?<!-- /spec:\1 -->", re.S)
NODE = re.compile(r'\b([A-Za-z]\w*)\s*[\[\(\{>/\\]+"([^"]+)"[\]\)\}/\\]+:::(\w+)')
CLASSDEF = re.compile(r"^\s*classDef\s+(\w+)\s+(.+?);?\s*$", re.M)
ARROW = re.compile(r"--|==|-\.")
GLOSSARY_ROW = re.compile(
    r'^\|\s*<a id="(per|ent|sys|term|st)-([a-z0-9-]+)"></a>([^|]*)\|([^|]*)\|([^|]*)\|\s*$')
TOKEN_ROW = re.compile(r"^\|\s*`([a-z]+(?:\.[a-z0-9-]+)+)`\s*\|\s*`([^`]+)`\s*\|(?:\s*`([^`]+)`\s*\|)?", re.M)
STATUS = re.compile(r"^\*\*Status:\*\* (.+?)(?:\s+·.*)?\s*$", re.M)
RULE_TYPE = re.compile(r"\*\*Type:\*\* ([^·\n]+?)\s*(?:·|$)", re.M)
ID_FILE = re.compile(r"^(FS|UC|BR)-(\d{3})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")


@dataclass
class Page:
    path: Path
    kind: str
    text: str

    @property
    def rel(self) -> str:
        return self.path.relative_to(ROOT).as_posix()

    @property
    def heading(self) -> str:
        match = H1.search(strip_fences(self.text))
        return match.group(1).strip() if match else self.path.stem

    @property
    def title(self) -> str:
        return strip_icon(self.heading) or self.path.stem

    @property
    def ident(self) -> str:
        match = ID_FILE.match(self.path.name)
        return f"{match.group(1)}-{match.group(2)}" if match else ""

    @property
    def status(self) -> str:
        match = STATUS.search(self.text)
        return match.group(1).strip() if match else ""


@dataclass
class Link:
    text: str
    target: str
    path: Optional[Path]
    fragment: str


@dataclass
class Term:
    anchor: str
    kind: str
    name: str
    aliases: List[str]

    @property
    def owner(self) -> str:
        return self.name.split(":", 1)[0].strip() if self.kind == "state" else ""


@dataclass
class Node:
    ident: str
    label: str
    cls: str

    @property
    def name(self) -> str:
        return strip_icon(re.split(r"<br\s*/?>", self.label)[0])


# Text helpers ----------------------------------------------------------------------------------------------------


def strip_fences(text: str) -> str:
    return FENCE.sub("", text)


def strip_blocks(text: str, names: Optional[Set[str]] = None) -> str:
    return BLOCK_ANY.sub(lambda m: "" if names is None or m.group(1) in names else m.group(0), text)


def strip_icon(text: str) -> str:
    return re.sub(r"^[^\w]+", "", text.replace("*", "").replace("`", "")).strip()


def set_block(text: str, name: str, content: str) -> str:
    pattern = re.compile(rf"(<!-- spec:{re.escape(name)} -->\n).*?(<!-- /spec:{re.escape(name)} -->)", re.S)
    inner = content.rstrip("\n") + "\n" if content else ""
    return pattern.sub(lambda m: m.group(1) + inner + m.group(2), text, count=1)


def has_block(text: str, name: str) -> bool:
    return f"<!-- spec:{name} -->\n" in text and f"<!-- /spec:{name} -->" in text


def section(text: str, anchor: str) -> str:
    start = re.search(rf'^## <a id="{re.escape(anchor)}"></a>.*$', text, re.M)
    if not start:
        return ""
    rest = text[start.end():]
    end = re.search(r"^(## |<!-- spec:nav-bottom)", rest, re.M)
    return rest[: end.start()] if end else rest


def relpath(source: Path, target: Path) -> str:
    return os.path.relpath(target, source.parent).replace(os.sep, "/")


def slugify(title: str) -> str:
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-") or "untitled"


def resolve(page: Page, target: str) -> Tuple[Optional[Path], str]:
    if re.match(r"^[a-z][a-z0-9+.-]*:", target):
        return None, ""
    file_part, _, fragment = target.partition("#")
    return ((page.path.parent / file_part).resolve() if file_part else page.path), fragment


def links(page: Page, text: Optional[str] = None) -> List[Link]:
    body = re.sub(r"`[^`\n]*`", "", strip_fences(page.text if text is None else text))
    found: List[Link] = []
    for match in LINK.finditer(body):
        path, fragment = resolve(page, match.group(2))
        found.append(Link(match.group(1), match.group(2), path, fragment))
    return found


def images(page: Page, text: Optional[str] = None) -> List[Link]:
    body = re.sub(r"`[^`\n]*`", "", strip_fences(page.text if text is None else text))
    found: List[Link] = []
    for match in IMAGE.finditer(body):
        path, fragment = resolve(page, match.group(2))
        found.append(Link(match.group(1), match.group(2), path, fragment))
    return found


def h2s(text: str) -> List[Tuple[Optional[str], str]]:
    headings: List[Tuple[Optional[str], str]] = []
    for line in H2.findall(strip_fences(strip_blocks(text, {"summary"}))):
        match = H2_ANCHORED.match(line)
        headings.append((match.group(1), match.group(2).strip()) if match else (None, line.strip()))
    return headings


def flowchart(text: str) -> Optional[str]:
    charts = [c for c in MERMAID.findall(section(text, "flowchart")) if c.split()[0:1] in (["flowchart"], ["graph"])]
    return charts[0] if charts else None


def nodes(chart: str) -> List[Node]:
    return [Node(ident, label, cls) for ident, label, cls in NODE.findall(chart)]


# Discovery, glossary and tokens ----------------------------------------------------------------------------------


def kind_of(path: Path) -> Optional[str]:
    rel = path.relative_to(SPECS).as_posix()
    for kind, (fixed, _, _) in FIXED_PAGES.items():
        if rel == fixed:
            return kind
    if rel.startswith("technical/"):
        return "technical-page"
    if rel.startswith("roadmap/"):
        return "roadmap-page"
    for kind, (folder, _, _) in KINDS.items():
        if rel.startswith(folder + "/") and "/" not in rel[len(folder) + 1:]:
            return kind
    return None


def discover() -> Tuple[List[Page], List[Path]]:
    pages: List[Page] = []
    unknown: List[Path] = []
    for path in sorted(SPECS.rglob("*.md")) if SPECS.is_dir() else []:
        kind = kind_of(path)
        if kind is None:
            unknown.append(path)
        else:
            pages.append(Page(path, kind, path.read_text(encoding="utf-8")))
    pages.sort(key=lambda p: (ORDER.index(p.kind), p.path.name if p.kind in KINDS else p.rel))
    return pages, unknown


def parse_glossary(text: str) -> Tuple[Dict[str, Term], List[str]]:
    terms: Dict[str, Term] = {}
    problems: List[str] = []
    names: Set[str] = set()
    for line in text.splitlines():
        match = GLOSSARY_ROW.match(line)
        if not match:
            if re.match(r"^\|\s*<a id=", line):
                problems.append(f"glossary row not in the expected format: {line.strip()}")
            continue
        prefix, slug, name_cell, definition, aliases = match.groups()
        anchor, name = f"{prefix}-{slug}", strip_icon(name_cell)
        if not name or not definition.strip():
            problems.append(f"row {anchor} needs a bold name and a definition.")
        if anchor in terms or name.lower() in names:
            problems.append(f"'{name}' ({anchor}) is defined twice.")
        names.add(name.lower())
        alias_list = [a.strip() for a in aliases.split(",") if a.strip() and a.strip() != "-"]
        terms[anchor] = Term(anchor, GLOSSARY_KINDS[prefix], name, alias_list)
    return terms, problems


def parse_tokens(pages: List[Page], mode: str = "light") -> Dict[str, str]:
    identity = next((p for p in pages if p.kind == "identity"), None)
    rows = TOKEN_ROW.findall(strip_fences(identity.text)) if identity else []
    return {name: (dark if mode == "dark" and dark else light) for name, light, dark in rows}


def dark_tokens(pages: List[Page]) -> Set[str]:
    identity = next((p for p in pages if p.kind == "identity"), None)
    rows = TOKEN_ROW.findall(strip_fences(identity.text)) if identity else []
    return {name for name, _, dark in rows if dark}


def palette(tokens: Dict[str, str]) -> Dict[str, str]:
    styles: Dict[str, str] = {}
    for cls, (main, soft, ink) in DEFAULT_COLOURS.items():
        main = tokens.get(f"color.{cls}", main)
        soft = tokens.get(f"color.{cls}-soft", soft)
        ink = tokens.get(f"color.{cls}-ink", ink)
        width = ",stroke-width:2px" if cls in BOLD_CLASSES else ""
        styles[cls] = f"fill:{soft},stroke:{main}{width},color:{ink}"
    return styles


def identity_css(tokens: Dict[str, str], dark: Dict[str, str]) -> str:
    lines = ["/* Generated by specs.py build from docs/specs/visual-identity.md. Do not edit: change the tokens there. */",
             ":root {", "  color-scheme: light dark;"]
    lines += [f"  --{name.replace('.', '-')}: {value};" for name, value in tokens.items()]
    lines += ["}", "", "@media (prefers-color-scheme: dark) {", "  :root {"]
    lines += [f"    --{name.replace('.', '-')}: {value};" for name, value in dark.items() if value != tokens.get(name)]
    return "\n".join(lines + ["  }", "}", ""])


def screen_size(tokens: Dict[str, str]) -> Optional[Tuple[int, int]]:
    width = re.fullmatch(r"(\d+)px", tokens.get("screen.width", ""))
    height = re.fullmatch(r"(\d+)px", tokens.get("screen.height", ""))
    return (int(width.group(1)), int(height.group(1))) if width and height else None
