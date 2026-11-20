#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import posixpath
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

sys.path.insert(0, str(Path(__file__).resolve().parent))

from roadmap_gantt import GRAPH, ROADMAP, cells, expand, key, short
from ticket_tree import find_home, main_checkout, open_states
from tickets import develop_ref, done_tickets, finished_tickets

USAGE = """Mirror the roadmap on GitHub: issues, sub-issues, "blocked by" links and the Kanban project (TKT-15).

Usage, from the repository root:
    python3 .claude/scripts/board.py bootstrap [--dry-run]
    python3 .claude/scripts/board.py move --ticket T0.09 --status running
    python3 .claude/scripts/board.py sync
    python3 .claude/scripts/board.py show [--all]

``bootstrap`` creates, once and in this order, what does not exist yet: the labels, one milestone per phase, the
project "Swarm roadmap" with its Status columns and views, one issue per phase, epic and ticket, the sub-issue tree
(phase > epic > ticket), a "blocked by" link per prerequisite of ``docs/specs/roadmap/gantt/ticket-graph.json``,
every issue on the project with its status, and the merged tickets closed. Every step is recorded in
``.claude/github.json`` as soon as it is done, so a stop (GitHub throttles content creation) is resumed by running it
again. ``move`` sets one ticket's column, ``sync`` recomputes Ready, the parents' columns and the closed issues from
the tickets merged on ``develop``, and ``show`` prints the board from the local cache ``.git/swarm/board.json``.

Columns: 📥 Backlog (prerequisites open), ✅ Ready (every prerequisite merged), 📝 Planned (PLAN.md awaits approval),
🔄 Running (``/ticket-run``), 👀 In review (pull request open), 🏁 Done (merged into ``develop``).
"""

Json = Union[None, bool, int, float, str, List["Json"], Dict[str, "Json"]]

ROOT = Path(__file__).resolve().parents[2]
MAIN = main_checkout(ROOT)
STATE = MAIN / ".claude" / "github.json"
CACHE_DIR = (
    Path(
        subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )
    / "swarm"
)
CACHE = CACHE_DIR / "board.json"
REPO = "gpbcom/swarm"
BRANCH = "develop"
BLOB = f"https://github.com/{REPO}/blob/{BRANCH}/docs/specs/roadmap/"
PROJECT_TITLE = "Swarm roadmap"
PAUSE_S = 1.0
ALREADY_LINKED = re.compile(
    r"already been taken|already exists|already a sub-issue|duplicate sub-issue|closed by another request",
    re.IGNORECASE,
)
STATUSES = [
    ("backlog", "📥 Backlog", "GRAY", "Waits for a prerequisite ticket"),
    ("ready", "✅ Ready", "BLUE", "Every prerequisite merged: can start"),
    ("planned", "📝 Planned", "PURPLE", "PLAN.md written, awaits approval"),
    ("running", "🔄 Running", "YELLOW", "The agents work in its worktree"),
    ("review", "👀 In review", "ORANGE", "Pull request open, CI running"),
    ("done", "🏁 Done", "GREEN", "Merged into develop"),
]
DEFAULT_OPTIONS = {"Todo": "backlog", "In Progress": "running", "Done": "done"}
PHASE_PAGES = sorted(p.name for p in ROADMAP.glob("0[1-8]-*.md"))
PHASE_COLOURS = ["5b6b7f", "1d4ed8", "0e7490", "6d28d9", "15803d", "4338ca", "c2410c", "b45309"]
LABELS = {
    "type:phase": ("0f172a", "A phase of the roadmap"),
    "type:epic": ("475569", "An epic of a phase"),
    "type:ticket": ("94a3b8", "A roadmap ticket, worked by the harness"),
    "size:S": ("d1fae5", "Small ticket"),
    "size:M": ("fef3c7", "Medium ticket"),
    "size:L": ("fee2e2", "Large ticket"),
    "critical-path": ("b91c1c", "On the critical path of the parallel plan"),
    "field": ("b45309", "Acceptance needs a flight, hardware, a partner or an authorisation"),
}
VIEWS = [("🗂️ Tickets board", "BOARD_LAYOUT", 'label:"type:ticket"'), ("📋 All issues", "TABLE_LAYOUT", "")]
ICON = {s[0]: s[1].split()[0] for s in STATUSES}


def git_ahead(home: Path) -> bool:
    """Tell whether a ticket's worktree holds its commit already (finish ran: the pull request is open)."""
    result = subprocess.run(
        ["git", "-C", str(home), "rev-list", "--count", "origin/develop..HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() not in ("", "0")


################
# GitHub calls #
################


def gh(args: List[str], payload: Optional[Json] = None, tolerate_existing: bool = False) -> Json:
    """Run ``gh`` and return its JSON output, waiting and retrying when GitHub throttles.

    With ``tolerate_existing``, a link GitHub already holds (made just before a stop, not yet recorded) counts as made:
    ``None`` is returned instead of stopping, so that a resumed bootstrap goes on.
    """
    for attempt in range(12):
        result = subprocess.run(
            ["gh", *args],
            input=json.dumps(payload) if payload is not None else None,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return json.loads(result.stdout) if result.stdout.strip() else None
        error = result.stderr + result.stdout
        if tolerate_existing and ALREADY_LINKED.search(error):
            return None
        if re.search(
            r"rate limit|abuse|was submitted too quickly|HTTP 403|HTTP 429|HTTP 502|timeout", error, re.IGNORECASE
        ):
            wait = min(60 * (attempt + 1), 600)
            print(f"   ⏳ GitHub throttles ({error.strip().splitlines()[-1][:80]}), waiting {wait} s", flush=True)
            time.sleep(wait)
            continue
        raise SystemExit(f"gh {' '.join(args[:3])} failed: {error.strip()}")
    raise SystemExit("GitHub kept throttling: run the same command again later, it resumes.")


def gql(query: str, *, tolerate_existing: bool = False, **variables: Json) -> Dict[str, Json]:
    data = gh(["api", "graphql", "--input", "-"], {"query": query, "variables": variables}, tolerate_existing)
    if data is None and tolerate_existing:
        return {}
    assert isinstance(data, dict)
    if data.get("errors"):
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]  # type: ignore[return-value]


def rest(method: str, path: str, payload: Optional[Json] = None, tolerate_existing: bool = False) -> Json:
    args = ["api", "-X", method, path, "--input", "-"] if payload is not None else ["api", "-X", method, path]
    return gh(args, payload, tolerate_existing)


#########
# State #
#########


def load_state() -> Dict[str, Json]:
    if STATE.is_file():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"repo": REPO, "milestones": {}, "issues": {}, "subissues": [], "blocked": [], "items": {}, "closed": []}


def save(state: Dict[str, Json]) -> None:
    STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


###########
# Roadmap #
###########


def absolute(text: str, page: str) -> str:
    """Rewrite the relative links of a roadmap cell to GitHub links, so they work in an issue."""

    def fix(match: re.Match) -> str:
        label, target = match.group(1), match.group(2)
        if re.match(r"^[a-z]+:", target):
            return match.group(0)
        if target.startswith("#"):
            return f"[{label}]({BLOB}{page}{target})"
        return f"[{label}]({BLOB}{posixpath.normpath(target)})"

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", fix, text).replace("<br>", "\n")


def roadmap() -> Tuple[List[Dict[str, str]], List[Dict[str, str]], List[Dict[str, str]]]:
    """Return the phases, the epics and the tickets of the roadmap, read from its pages."""
    readme = (ROADMAP / "README.md").read_text(encoding="utf-8")
    phases, epics, tickets = [], [], []
    for number, page in enumerate(PHASE_PAGES):
        text = (ROADMAP / page).read_text(encoding="utf-8")
        title = re.search(r"^# \S+ (P\d+): (.+)$", text, re.MULTILINE)
        note = re.search(r"^> \[!NOTE\]\n> (.+)$", text, re.MULTILINE)
        dates = re.search(
            rf"^\s+P{number} [^:]+:p{number}, (\d{{4}}-\d\d-\d\d), (\d{{4}}-\d\d-\d\d)", readme, re.MULTILINE
        )
        phases.append(
            {
                "id": f"P{number}",
                "name": title.group(2),
                "page": page,
                "note": note.group(1) if note else "",
                "start": dates.group(1) if dates else "",
                "end": dates.group(2) if dates else "",
            }
        )
        epic_of: Dict[str, str] = {}
        sprint_of: Dict[str, str] = {}
        for line in text.splitlines():
            row = cells(line) if line.startswith("|") else []
            if row and re.match(r"^E\d+\.\d+$", row[0]) and len(row) >= 5:
                epics.append(
                    {
                        "id": row[0],
                        "phase": f"P{number}",
                        "name": row[1],
                        "page": page,
                        "delivers": absolute(row[2], page),
                        "where": absolute(row[3], page),
                        "tasks": absolute(row[5], page) if len(row) > 5 else "",
                    }
                )
                for ticket in expand(re.sub(r"\]\(#[^)]+\)", "", row[4].replace("[", ""))):
                    epic_of.setdefault(ticket, row[0])
            match = re.match(r"^\[?(S\d+)", row[0]) if row else None
            if match and len(row) > 2 and re.search(r"T\d+\.\d+", row[2]):
                for ticket in expand(row[2]):
                    sprint_of.setdefault(ticket, match.group(1))
        seen = set()
        for line in text.splitlines():
            row = cells(line) if line.startswith("|") else []
            match = re.match(r"^\**\[?(T(\d+)\.\d+)\]?(?:\(#[^)]+\))?\**\s*(.*)$", row[0]) if row else None
            if not match or int(match.group(2)) != number or match.group(1) in seen:
                continue
            seen.add(match.group(1))
            if len(row) >= 5 and re.match(r"^S\d+$", row[1]):
                epic = re.sub(r"[\[\]]|\(#[^)]+\)", "", row[2])
                tickets.append(
                    {
                        "id": match.group(1),
                        "phase": f"P{number}",
                        "sprint": row[1],
                        "epic": epic,
                        "title": short(row[3]),
                        "delivers": absolute(row[3], page),
                        "where": "",
                        "done_when": absolute(row[4], page),
                        "page": page,
                    }
                )
            else:
                tickets.append(
                    {
                        "id": match.group(1),
                        "phase": f"P{number}",
                        "sprint": sprint_of.get(match.group(1), ""),
                        "epic": epic_of.get(match.group(1), ""),
                        "title": short(match.group(3) or row[1]),
                        "delivers": absolute(row[1], page),
                        "where": absolute(row[2], page),
                        "done_when": absolute(row[-1], page),
                        "page": page,
                    }
                )
    return phases, epics, tickets


class Board:
    """The roadmap, its ticket graph, the merged tickets, and their mirror on GitHub."""

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.state = load_state()
        self.phases, self.epics, self.tickets = roadmap()
        self.graph = json.loads(GRAPH.read_text(encoding="utf-8"))
        self.done = set(done_tickets(MAIN))
        self.finished = finished_tickets(MAIN, develop_ref(MAIN))
        self.open = set(open_states(MAIN))
        self.by_id = {t["id"]: t for t in self.tickets}
        self.external = {item[0]: item for items in self.graph["external_items"].values() for item in items}
        self.critical = self.critical_path()

    def critical_path(self) -> List[str]:
        html = ROADMAP / "gantt" / "parallel-plan.html"
        match = re.search(r'"crit":\[([^\]]*)\]', html.read_text(encoding="utf-8")) if html.is_file() else None
        return re.findall(r"T\d+\.\d+", match.group(1)) if match else []

    ##########
    # Status #
    ##########

    def local_status(self, ticket: str) -> str:
        """Return the column a ticket's own state on disk gives it."""
        if ticket in self.done:
            return "done"
        home = find_home(ROOT, ticket)
        folder = (home or MAIN) / "docs" / "tickets" / ticket
        progress = (folder / "PROGRESS.md").read_text(encoding="utf-8") if (folder / "PROGRESS.md").is_file() else ""
        if ticket in self.finished or re.search(r"In review|Pull request", progress):
            return "review"
        if home is not None and git_ahead(home):
            return "review"
        if ticket in self.open or home is not None or re.search(r"\*\*Status:\*\* 🔄", progress):
            return "running"
        plan = folder / "PLAN.md"
        if plan.is_file() and "Awaiting approval" in plan.read_text(encoding="utf-8"):
            return "planned"
        if plan.is_file() and "🟢 Approved" in plan.read_text(encoding="utf-8"):
            return "planned"
        deps = self.graph["tickets"][ticket]["deps"]
        return (
            "ready" if all(d in self.done for d in deps) and "field" not in self.graph["tickets"][ticket] else "backlog"
        )

    def parent_status(self, children: List[str], statuses: Dict[str, str]) -> str:
        values = [statuses[c] for c in children if c in statuses]
        if values and all(v == "done" for v in values):
            return "done"
        if any(v != "backlog" for v in values):
            return "running"
        return "backlog"

    def statuses(self) -> Dict[str, str]:
        """Return the column of every phase, epic and ticket."""
        cached = json.loads(CACHE.read_text(encoding="utf-8")).get("status", {}) if CACHE.is_file() else {}
        result: Dict[str, str] = {}
        for ticket in self.tickets:
            local = self.local_status(ticket["id"])
            kept = cached.get(ticket["id"])
            result[ticket["id"]] = kept if kept in ("running", "review") and local not in ("done",) else local
        for epic in self.epics:
            result[epic["id"]] = self.parent_status([t["id"] for t in self.tickets if t["epic"] == epic["id"]], result)
        for phase in self.phases:
            result[phase["id"]] = self.parent_status([e["id"] for e in self.epics if e["phase"] == phase["id"]], result)
        return result

    ##########
    # Bodies #
    ##########

    def ticket_body(self, ticket: Dict[str, str]) -> str:
        info = self.graph["tickets"][ticket["id"]]
        phase = next(p for p in self.phases if p["id"] == ticket["phase"])
        lines = [
            "> [!NOTE]",
            (
                f"> Roadmap ticket of [🛣️ {phase['id']}: {phase['name']}]({BLOB}{ticket['page']}#sprints), "
                f"sprint {ticket['sprint']}, epic {ticket['epic']}. Worked by the harness: `/ticket-plan {ticket['id']}`, "
                f"then `/ticket-run {ticket['id']}`."
            ),
            "",
            "### 📦 Delivers",
            "",
            ticket["delivers"],
            "",
        ]
        if ticket["where"]:
            lines += ["### 🗂️ Where", "", ticket["where"], ""]
        lines += ["### ✅ Done when", "", ticket["done_when"], ""]
        if info["deps"]:
            lines += ["### ⛓️ Needs", "", "Shown as **Blocked by** links: " + ", ".join(info["deps"]) + ".", ""]
        if info["external"]:
            links = [f"[{e}]({BLOB}{self.external[e][3]})" if e in self.external else e for e in info["external"]]
            lines += [
                "### 🛫 Field acceptance",
                "",
                "Built and tested on the Simulator first, accepted with " + ", ".join(links) + ".",
                "",
            ]
        lines += [
            (
                f"**Size:** {info['size']} · **Areas:** {info['area'] or '➖'} · "
                f"[⛓️ Parallel plan]({BLOB}14-parallel-plan.md)"
            ),
            "",
            f"<!-- swarm:id={ticket['id']} -->",
        ]
        return "\n".join(lines)

    def epic_body(self, epic: Dict[str, str]) -> str:
        return "\n".join(
            [
                "> [!NOTE]",
                f"> Epic of [🛣️ {epic['phase']}]({BLOB}{epic['page']}#epics). Its tickets are its sub-issues.",
                "",
                "### 📦 Delivers",
                "",
                epic["delivers"],
                "",
                "### 🗂️ Where",
                "",
                epic["where"],
                "",
                "### 🧑‍💻 Parallel tasks for the agents",
                "",
                epic["tasks"] or "➖",
                "",
                f"<!-- swarm:id={epic['id']} -->",
            ]
        )

    def phase_body(self, phase: Dict[str, str]) -> str:
        return "\n".join(
            [
                "> [!NOTE]",
                f"> {absolute(phase['note'], phase['page'])}",
                "",
                (
                    f"**Roadmap dates:** {phase['start']} to {phase['end']} · [🛣️ Phase page]({BLOB}{phase['page']}) · "
                    f"[⛓️ Parallel plan]({BLOB}14-parallel-plan.md)"
                ),
                "",
                "Its epics are its sub-issues.",
                "",
                f"<!-- swarm:id={phase['id']} -->",
            ]
        )

    #############
    # Bootstrap #
    #############

    def step(self, message: str) -> None:
        print(message, flush=True)
        if not self.dry_run:
            save(self.state)
            time.sleep(PAUSE_S)

    def labels(self) -> None:
        wanted = dict(LABELS)
        for number, _ in enumerate(PHASE_PAGES):
            wanted[f"phase:P{number}"] = (PHASE_COLOURS[number], f"Phase P{number} of the roadmap")
        if self.dry_run:
            print(f"🏷️  {len(wanted)} labels")
            return
        existing = {label["name"] for label in gh(["label", "list", "-R", REPO, "--limit", "200", "--json", "name"])}
        for name, (colour, description) in wanted.items():
            if name not in existing and not self.dry_run:
                gh(["label", "create", name, "-R", REPO, "--color", colour, "--description", description])
                self.step(f"🏷️  label {name}")

    def milestones(self) -> None:
        for phase in self.phases:
            if phase["id"] in self.state["milestones"]:
                continue
            title = f"{phase['id']}: {phase['name']}"
            if self.dry_run:
                print(f"🏆 milestone {title}")
                continue
            created = rest(
                "POST",
                f"repos/{REPO}/milestones",
                {"title": title, "due_on": f"{phase['end']}T23:59:59Z", "description": phase["note"][:500]},
            )
            self.state["milestones"][phase["id"]] = created["number"]
            self.step(f"🏆 milestone {title}")

    def project(self) -> None:
        if self.state.get("project") or self.dry_run:
            return
        owner = gql("query($login:String!){ user(login:$login){ id } }", login=REPO.split("/")[0])["user"]["id"]
        project = gql(
            "mutation($o:ID!,$t:String!){ createProjectV2(input:{ownerId:$o,title:$t}){ projectV2{ id number url } } }",
            o=owner,
            t=PROJECT_TITLE,
        )["createProjectV2"]["projectV2"]
        repo_id = gql('query{ repository(owner:"gpbcom",name:"swarm"){ id } }')["repository"]["id"]
        gql(
            "mutation($p:ID!,$r:ID!){ linkProjectV2ToRepository(input:{projectId:$p,repositoryId:$r}){ clientMutationId } }",
            p=project["id"],
            r=repo_id,
        )
        field = gql(
            """query($p:ID!){ node(id:$p){ ... on ProjectV2 { field(name:"Status"){ ... on ProjectV2SingleSelectField {
                    id options{ id name } } } } } }""",
            p=project["id"],
        )["node"]["field"]
        by_key = {DEFAULT_OPTIONS[o["name"]]: o["id"] for o in field["options"] if o["name"] in DEFAULT_OPTIONS}
        options = [
            {"name": name, "color": colour, "description": text, **({"id": by_key[k]} if k in by_key else {})}
            for k, name, colour, text in STATUSES
        ]
        updated = gql(
            """mutation($f:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]){ updateProjectV2Field(input:{fieldId:$f,
                      singleSelectOptions:$o}){ projectV2Field{ ... on ProjectV2SingleSelectField { options{ id name } } } } }""",
            f=field["id"],
            o=options,
        )["updateProjectV2Field"]["projectV2Field"]["options"]
        names = {name: k for k, name, _, _ in STATUSES}
        self.state["project"] = {
            "id": project["id"],
            "number": project["number"],
            "url": project["url"],
            "status_field": field["id"],
            "status": {names[o["name"]]: o["id"] for o in updated},
        }
        for name, layout, query in VIEWS:
            view = gql(
                "mutation($p:ID!,$n:String!,$l:ProjectV2ViewLayout!){ createProjectV2View(input:{projectId:$p,name:$n,"
                "layout:$l}){ projectV2View{ id } } }",
                p=project["id"],
                n=name,
                l=layout,
            )
            if query:
                gql(
                    "mutation($v:ID!,$f:String!){ updateProjectV2View(input:{viewId:$v,filter:$f}){ clientMutationId } }",
                    v=view["createProjectV2View"]["projectV2View"]["id"],
                    f=query,
                )
        self.step(f"🗂️  project {project['url']}")

    def create_issue(self, ident: str, title: str, body: str, labels: List[str], phase: str) -> None:
        if ident in self.state["issues"]:
            return
        if self.dry_run:
            print(f"📝 issue {title}")
            return
        payload = {"title": title, "body": body, "labels": labels, "milestone": self.state["milestones"][phase]}
        created = rest("POST", f"repos/{REPO}/issues", payload)
        self.state["issues"][ident] = {"number": created["number"], "node": created["node_id"], "db": created["id"]}
        self.step(f"📝 #{created['number']} {title}")

    def ticket_order(self) -> List[Dict[str, str]]:
        """Return the tickets with every prerequisite before the tickets that need it."""
        placed: List[str] = []
        pending = sorted(self.by_id, key=key)
        while pending:
            for ticket in list(pending):
                if all(d in placed or d not in self.by_id for d in self.graph["tickets"][ticket]["deps"]):
                    placed.append(ticket)
                    pending.remove(ticket)
        return [self.by_id[t] for t in placed]

    def issues(self) -> None:
        for phase in self.phases:
            self.create_issue(
                phase["id"],
                f"{phase['id']}: {phase['name']}",
                self.phase_body(phase),
                ["type:phase", f"phase:{phase['id']}"],
                phase["id"],
            )
        for epic in self.epics:
            self.create_issue(
                epic["id"],
                f"{epic['id']}: {epic['name']}",
                self.epic_body(epic),
                ["type:epic", f"phase:{epic['phase']}"],
                epic["phase"],
            )
        for ticket in self.ticket_order():
            info = self.graph["tickets"][ticket["id"]]
            labels = ["type:ticket", f"phase:{ticket['phase']}", f"size:{info['size']}"]
            labels += ["critical-path"] if ticket["id"] in self.critical else []
            labels += ["field"] if info["external"] or "field" in info else []
            self.create_issue(
                ticket["id"], f"{ticket['id']}: {ticket['title']}", self.ticket_body(ticket), labels, ticket["phase"]
            )

    def links(self) -> None:
        pairs = [(e["phase"], e["id"]) for e in self.epics] + [(t["epic"], t["id"]) for t in self.tickets if t["epic"]]
        for parent, child in pairs:
            if [parent, child] in self.state["subissues"] or self.dry_run:
                continue
            gql(
                "mutation($i:ID!,$s:ID!){ addSubIssue(input:{issueId:$i,subIssueId:$s}){ clientMutationId } }",
                tolerate_existing=True,
                i=self.state["issues"][parent]["node"],
                s=self.state["issues"][child]["node"],
            )
            self.state["subissues"].append([parent, child])
            self.step(f"🌳 {parent} › {child}")
        for ticket in self.ticket_order():
            for dep in self.graph["tickets"][ticket["id"]]["deps"]:
                if [ticket["id"], dep] in self.state["blocked"] or self.dry_run:
                    continue
                gql(
                    "mutation($i:ID!,$b:ID!){ addBlockedBy(input:{issueId:$i,blockingIssueId:$b}){ clientMutationId } }",
                    tolerate_existing=True,
                    i=self.state["issues"][ticket["id"]]["node"],
                    b=self.state["issues"][dep]["node"],
                )
                self.state["blocked"].append([ticket["id"], dep])
                self.step(f"⛓️  {ticket['id']} blocked by {dep}")

    def set_status(self, ident: str, status: str) -> None:
        project = self.state["project"]
        item = self.state["items"].get(ident, {})
        if not item.get("id"):
            added = gql(
                "mutation($p:ID!,$c:ID!){ addProjectV2ItemById(input:{projectId:$p,contentId:$c}){ item{ id } } }",
                p=project["id"],
                c=self.state["issues"][ident]["node"],
            )
            item = {"id": added["addProjectV2ItemById"]["item"]["id"]}
        if item.get("status") != status:
            gql(
                """mutation($p:ID!,$i:ID!,$f:ID!,$o:String!){ updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i,
                fieldId:$f,value:{singleSelectOptionId:$o}}){ clientMutationId } }""",
                p=project["id"],
                i=item["id"],
                f=project["status_field"],
                o=project["status"][status],
            )
            item["status"] = status
        self.state["items"][ident] = item
        self.step(f"{ICON[status]} {ident} → {status}")

    def close(self, ident: str, done: bool) -> None:
        if done and ident not in self.state["closed"]:
            rest(
                "PATCH",
                f"repos/{REPO}/issues/{self.state['issues'][ident]['number']}",
                {"state": "closed", "state_reason": "completed"},
                tolerate_existing=True,
            )
            self.state["closed"].append(ident)
            self.step(f"🏁 closed {ident}")

    def place(self) -> None:
        statuses = self.statuses()
        for ident, status in statuses.items():
            if self.dry_run:
                continue
            if self.state["items"].get(ident, {}).get("status") != status:
                self.set_status(ident, status)
            self.close(ident, status == "done")
        self.write_cache(statuses)

    def bootstrap(self) -> None:
        self.labels()
        self.milestones()
        self.project()
        self.issues()
        self.links()
        self.place()
        if self.dry_run:
            deps = sum(len(v["deps"]) for v in self.graph["tickets"].values())
            print(f"{len(self.phases)} phases, {len(self.epics)} epics, {len(self.tickets)} tickets, {deps} blocked-by")
        else:
            print(f"✅ Board ready: {self.state['project']['url']}")

    ########
    # Show #
    ########

    def write_cache(self, statuses: Dict[str, str]) -> None:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        numbers = {k: v["number"] for k, v in self.state.get("issues", {}).items()}
        titles = {t["id"]: t["title"] for t in self.tickets}
        CACHE.write_text(
            json.dumps(
                {
                    "status": statuses,
                    "numbers": numbers,
                    "titles": titles,
                    "project": self.state.get("project", {}).get("url", ""),
                    "updated": time.strftime("%Y-%m-%d %H:%M"),
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def move(self, ticket: str, status: str) -> None:
        statuses = self.statuses()
        statuses[ticket] = status
        if "project" in self.state and ticket in self.state["issues"]:
            self.set_status(ticket, status)
            epic = self.by_id[ticket]["epic"]
            for parent in (epic, self.by_id[ticket]["phase"]):
                if parent:
                    self.set_status(parent, statuses[parent])
        self.write_cache(statuses)
        print(f"{ICON[status]} {ticket} → { {k: n for k, n, _, _ in STATUSES}[status] }")


def show(include_all: bool) -> None:
    """Print the board from the local cache: counts per phase, then the tickets that move."""
    if not CACHE.is_file():
        raise SystemExit("No board cache yet: run python3 .claude/scripts/board.py sync")
    cache = json.loads(CACHE.read_text(encoding="utf-8"))
    status, numbers, titles = cache["status"], cache["numbers"], cache["titles"]
    tickets = sorted([t for t in status if re.match(r"^T\d+\.\d+$", t)], key=key)
    print(f"🗂️  Swarm roadmap · {cache['project']} · updated {cache['updated']}")
    print("      " + "".join(f"{s[1]:<14}" for s in STATUSES))
    for phase in range(8):
        mine = [t for t in tickets if t.startswith(f"T{phase}.")]
        counts = [sum(1 for t in mine if status[t] == s[0]) for s in STATUSES]
        bar = "".join(f"{(str(c) if c else '·'):<14}" for c in counts)
        print(f"  P{phase}  {bar}")
    for key_, name, _, _ in STATUSES[1:5] if not include_all else STATUSES:
        moving = [t for t in tickets if status[t] == key_]
        if moving:
            print(f"\n{name} ({len(moving)})")
            for t in moving[:40]:
                print(f"   #{numbers.get(t, '?'):<4} {t:<6} {titles.get(t, '')[:80]}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=USAGE.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    boot = sub.add_parser("bootstrap")
    boot.add_argument("--dry-run", action="store_true")
    move = sub.add_parser("move")
    move.add_argument("--ticket", required=True)
    move.add_argument("--status", required=True, choices=[s[0] for s in STATUSES])
    sub.add_parser("sync")
    view = sub.add_parser("show")
    view.add_argument("--all", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "show":
        show(args.all)
        return 0
    board = Board(dry_run=getattr(args, "dry_run", False))
    if args.command == "bootstrap":
        board.bootstrap()
    elif args.command == "move":
        board.move(args.ticket, args.status)
    else:
        board.place()
    return 0


if __name__ == "__main__":
    sys.exit(main())
