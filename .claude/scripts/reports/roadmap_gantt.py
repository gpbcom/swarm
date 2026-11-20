#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import heapq
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

USAGE = """Build the parallel plan of the roadmap: which tickets can run at the same time, and their Gantt charts.

Usage, from the repository root:
    python3 .claude/scripts/reports/roadmap_gantt.py build
    python3 .claude/scripts/reports/roadmap_gantt.py check

Inputs:
- the ticket rows of the eight phase pages ``docs/specs/roadmap/0[1-8]-*.md`` (sprint, title);
- ``docs/specs/roadmap/gantt/ticket-graph.json``: for each ticket, the tickets it needs (``deps``), the external items its
  acceptance needs, its areas, its size, and whether it only exists after a campaign (``field``); the external items
  with their dates; the hours per size; the scenarios (lanes, review factor);
- the tickets merged on ``develop``: those whose ``docs/tickets/<ID>/EXPLAIN.md`` is committed there (TKT-14), and the
  ``PROGRESS.md`` timings of those tickets (agent minutes and tokens).

The schedule starts on the day of the last merged ticket. Each scenario runs K lanes: a ticket starts when every ticket
it needs is merged and no open ticket shares one of its areas, holds its lane until it is merged, and one person
approves and reviews the tickets one after another. The ticket with the most work after it goes first.

``build`` writes ``docs/specs/roadmap/gantt/parallel-plan.html`` (interactive Gantt charts, from the template next to
this script) and the text between the ``<!-- gantt:plan -->`` markers of ``docs/specs/roadmap/14-parallel-plan.md``;
run ``specs.py build`` after it. ``check`` prints one line per stale output and exits 1, or prints nothing.
"""

ROOT = Path(__file__).resolve().parents[3]
ROADMAP = ROOT / "docs" / "specs" / "roadmap"
GRAPH = ROADMAP / "gantt" / "ticket-graph.json"
HTML = ROADMAP / "gantt" / "parallel-plan.html"
PAGE = ROADMAP / "14-parallel-plan.md"
TEMPLATE = Path(__file__).with_name("roadmap_gantt.html")
TICKETS = ROOT / "docs" / "tickets"
START = "<!-- gantt:plan -->"
END = "<!-- /gantt:plan -->"
PHASES = [
    "P0 Foundations",
    "P1 First flight",
    "P2 Inspection product",
    "P3 Patrol",
    "P4 Agriculture",
    "P5 AI agents",
    "P6 Light shows",
    "P7 Scale and reach",
]
PHASE_PAGES = [
    "01-p0-foundations.md",
    "02-p1-first-flight.md",
    "03-p2-inspection-product.md",
    "04-p3-patrol.md",
    "05-p4-agriculture.md",
    "06-p5-ai-agents.md",
    "07-p6-light-shows.md",
    "08-p7-scale-and-reach.md",
]
SCENARIO_NAMES = {
    "serial": "Today's harness, one ticket at a time",
    "k2": "2 tickets at once",
    "k3": "3 tickets at once",
    "k4": "4 tickets at once",
    "k4_light": "4 at once, lighter review",
    "k6_light": "6 at once, lighter review",
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
GROUP_TITLES = {
    "regulatory": "🏛️ Regulatory",
    "hardware": "🤝 Hardware",
    "partners": "🤝 Partners and providers",
    "campaigns": "🛫 Flight test campaigns",
    "milestones": "🏆 Milestones",
}
SERVICES = [
    "flight-engine",
    "missions",
    "gateway",
    "fleet",
    "agents",
    "processing",
    "evidence",
    "planner",
    "simulator",
    "video-relay",
    "notifier",
]
APPS = {
    "ground control": "frontends/ground-control",
    "mission studio": "frontends/mission-studio",
    "back office": "frontends/back-office",
    "client portal": "frontends/client-portal",
}
AREA = re.compile(
    r"(services/[\w-]+|frontends/[\w-]+|packages/\w+/[\w-]+|packages/\w+|deploy/[\w-]+|tests/[\w-]+"
    r"|\.github|\.claude)"
)
TICKET_ID = re.compile(r"T(\d+)\.(\d+)")


def key(ticket: str) -> Tuple[int, int]:
    """Sort ticket IDs by phase, then number."""
    match = TICKET_ID.match(ticket)
    return (int(match.group(1)), int(match.group(2))) if match else (99, 99)


def cells(line: str) -> List[str]:
    return [re.sub(r'<a id="[^"]+"></a>', "", cell).strip() for cell in line.strip().strip("|").split("|")]


def expand(text: str) -> List[str]:
    """Return the ticket IDs of a text, ``T0.01 to T0.03`` included."""
    found = [
        f"T{a}.{n:02d}"
        for a, b, c in re.findall(r"T(\d+)\.(\d+) to T\d+\.(\d+)", text)
        for n in range(int(b), int(c) + 1)
    ]
    return found + re.findall(r"T\d+\.\d+", text)


def short(text: str) -> str:
    """Shorten a ticket row to a title."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text).replace("`", "").replace("**", "")
    text = re.split(r"(?<=[a-z)]): |; | \((?!UC|BR|FS)|\. ", text)[0]
    return text[:110].rsplit(" ", 1)[0] + "…" if len(text) > 112 else text


def roadmap_rows() -> Dict[str, Dict[str, str]]:
    """Return each ticket's phase, sprint and title, read from the phase pages."""
    rows: Dict[str, Dict[str, str]] = {}
    for phase, name in enumerate(PHASE_PAGES):
        lines = (ROADMAP / name).read_text(encoding="utf-8").splitlines()
        sprint_of: Dict[str, str] = {}
        for line in lines:
            row = cells(line) if line.startswith("|") else []
            match = re.match(r"^\[?(S\d+)", row[0]) if row else None
            if match and len(row) > 2 and TICKET_ID.search(row[2]):
                for ticket in expand(row[2]):
                    sprint_of.setdefault(ticket, match.group(1))
        for line in lines:
            row = cells(line) if line.startswith("|") else []
            match = re.match(r"^\**\[?(T(\d+)\.\d+)\]?(?:\(#[^)]+\))?\**\s*(.*)$", row[0]) if row else None
            if not match or int(match.group(2)) != phase or match.group(1) in rows:
                continue
            if len(row) >= 5 and re.match(r"^S\d+$", row[1]):
                rows[match.group(1)] = {"phase": str(phase), "sprint": row[1], "title": short(row[3])}
            else:
                title = match.group(3) or row[1]
                rows[match.group(1)] = {
                    "phase": str(phase),
                    "sprint": sprint_of.get(match.group(1), ""),
                    "title": short(title),
                }
    return rows


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def develop_ref(root: Union[str, Path] = ROOT) -> str:
    """Return ``develop``, else ``origin/develop``, else ``HEAD`` (a CI checkout of a pull request has neither)."""
    for ref in ("develop", "origin/develop"):
        found = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", "--quiet", ref], capture_output=True, check=False
        )
        if found.returncode == 0:
            return ref
    return "HEAD"


def merged() -> Tuple[Set[str], dt.date]:
    """Return the tickets merged on develop and the day of the last one.

    A shallow checkout (CI) may not hold the commit that added the last ``EXPLAIN.md``: the day of ``ref`` is used.
    """
    ref = develop_ref()
    files = git("ls-tree", "-r", "--name-only", ref, "docs/tickets").split()
    done = {path.split("/")[2] for path in files if path.endswith("/EXPLAIN.md")}
    last = git("log", "-1", "--format=%ad", "--date=short", ref, "--", *[f"docs/tickets/{t}/EXPLAIN.md" for t in done])
    if not last.strip():
        last = git("log", "-1", "--format=%ad", "--date=short", ref)
    return done, dt.date.fromisoformat(last.strip())


def measured(done: Set[str]) -> Tuple[float, float]:
    """Return the mean agent minutes and the mean tokens (millions) of the merged tickets, from PROGRESS.md."""
    minutes: List[float] = []
    tokens: List[float] = []
    for ticket in done:
        progress = TICKETS / ticket / "PROGRESS.md"
        text = progress.read_text(encoding="utf-8") if progress.is_file() else ""
        agent = re.search(r"Time with agents working[^|]*\|\s*(?:(\d+)h)?(\d+)m", text)
        total = re.search(r"Tokens consumed[^|]*\|\s*\*\*([\d.]+)M\*\*", text)
        if agent:
            minutes.append(int(agent.group(1) or 0) * 60 + int(agent.group(2)))
        if total:
            tokens.append(float(total.group(1)))
    return (sum(minutes) / len(minutes) if minutes else 0.0, sum(tokens) / len(tokens) if tokens else 0.0)


def areas(text: str) -> Set[str]:
    """Return the areas a ticket changes; ``*`` when it may change any of them."""
    found = {area.rstrip("/") for area in AREA.findall(text)}
    found |= {f"services/{name}" for name in SERVICES if re.search(rf"(?<![/\w-]){name}\b", text)}
    found |= {path for name, path in APPS.items() if name in text.lower()}
    if "mavlink" in text:
        found.add("packages/rust")
    if not found or "any " in text or "every service" in text:
        return {"*"}
    return found


class Plan:
    """The ticket graph, its schedule per scenario, and what the outputs show."""

    def __init__(self) -> None:
        self.graph = json.loads(GRAPH.read_text(encoding="utf-8"))
        self.rows = roadmap_rows()
        self.done, self.as_of = merged()
        self.agent_minutes, self.tokens = measured(self.done)
        tickets = self.graph["tickets"]
        missing = sorted(set(self.rows) ^ set(tickets), key=key)
        if missing:
            raise SystemExit(f"ticket-graph.json and the phase pages differ on: {', '.join(missing)}")
        self.field = [t for t in tickets if "field" in tickets[t] and t not in self.done]
        self.soft = [t for t in tickets if t not in self.done and t not in self.field]
        self.deps = {t: [d for d in tickets[t]["deps"] if d in self.soft] for t in self.soft}
        self.size = {t: tickets[t]["size"] for t in tickets}
        self.areas = {t: areas(tickets[t]["area"]) for t in tickets}
        hours = self.graph["hours"]
        self.agent, self.human, self.per_day = hours["agent"], hours["human"], hours["per_day"]
        self.after: Dict[str, List[str]] = {t: [] for t in self.soft}
        for ticket in self.soft:
            for dep in self.deps[ticket]:
                self.after[dep].append(ticket)
        self.rank: Dict[str, float] = {}
        for ticket in sorted(self.soft, key=key, reverse=True):
            self.rank_of(ticket)
        self.critical = self.critical_path()
        self.wave: Dict[str, int] = {}
        for ticket in sorted(self.soft, key=key):
            self.wave_of(ticket)
        self.calendar = self.working_days(400)
        self.runs = {name: self.simulate(lanes, factor) for name, lanes, factor in self.graph["lanes"]}
        self.unlocked = self.simulate(6, 1.0, lock=False)

    def rank_of(self, ticket: str) -> float:
        if ticket not in self.rank:
            own = self.agent[self.size[ticket]] + self.human[self.size[ticket]]
            self.rank[ticket] = own + max([self.rank_of(t) for t in self.after[ticket]], default=0.0)
        return self.rank[ticket]

    def wave_of(self, ticket: str) -> int:
        if ticket not in self.wave:
            self.wave[ticket] = 1 + max([self.wave_of(d) for d in self.deps[ticket]], default=0)
        return self.wave[ticket]

    def critical_path(self) -> List[str]:
        path = [max(self.soft, key=lambda t: (self.rank[t], -key(t)[0]))]
        while self.after[path[-1]]:
            path.append(max(self.after[path[-1]], key=lambda t: self.rank[t]))
        return path

    def order(self, ticket: str) -> Tuple[float, int, Tuple[int, int]]:
        return (-self.rank[ticket], key(ticket)[0], key(ticket))

    def simulate(self, lanes: int, factor: float, lock: bool = True) -> Dict[str, Dict[str, float]]:
        """Return the start and merge hour of every ticket on ``lanes`` lanes, review time times ``factor``."""
        now, running, waiting, review = 0.0, [], [], None
        start: Dict[str, float] = {}
        end: Dict[str, float] = {}
        open_: Set[str] = set()
        pending = sorted(self.soft, key=self.order)
        while len(end) < len(self.soft):
            locked = set().union(*[self.areas[t] for t in open_]) if open_ else set()
            for ticket in [t for t in pending if all(d in end for d in self.deps[t])]:
                if len(open_) >= lanes:
                    break
                mine = self.areas[ticket]
                if lock and ("*" in locked or (locked and "*" in mine) or mine & locked):
                    continue
                start[ticket] = now
                open_.add(ticket)
                locked |= mine
                pending.remove(ticket)
                heapq.heappush(running, (now + self.agent[self.size[ticket]], key(ticket), ticket))
            if review is None and waiting:
                waiting.sort(key=self.order)
                ticket = waiting.pop(0)
                review = (now + self.human[self.size[ticket]] * factor, ticket)
            now = min(([running[0][0]] if running else []) + ([review[0]] if review else []))
            while running and running[0][0] <= now + 1e-9:
                waiting.append(heapq.heappop(running)[2])
            if review and review[0] <= now + 1e-9:
                end[review[1]] = now
                open_.discard(review[1])
                review = None
        return {"start": start, "end": end}

    def working_days(self, count: int) -> List[str]:
        days, day = [], self.as_of
        while len(days) < count:
            if day.weekday() < 5:
                days.append(day.isoformat())
            day += dt.timedelta(days=1)
        return days

    def date(self, hours: float) -> str:
        return self.calendar[min(len(self.calendar) - 1, int(hours / self.per_day + 1e-6))]

    def end(self, scenario: str) -> float:
        return max(self.runs[scenario]["end"].values())

    def busy(self, scenario: str) -> float:
        factor = next(f for n, _, f in self.graph["lanes"] if n == scenario)
        return sum(self.human[self.size[t]] * factor for t in self.soft) / self.end(scenario)

    def waiting_on(self, item: str) -> List[str]:
        tickets = self.graph["tickets"]
        return [t for t in sorted(tickets, key=key) if item in tickets[t]["external"] and t in self.soft]

    ##########
    # Output #
    ##########

    def data(self) -> Dict[str, object]:
        """Return what the interactive page draws."""
        tickets = self.graph["tickets"]
        rows = []
        for ticket in sorted(tickets, key=key):
            if ticket in self.done:
                continue
            info = tickets[ticket]
            row = {
                "id": ticket,
                "p": int(self.rows[ticket]["phase"]),
                "ti": self.rows[ticket]["title"],
                "sz": info["size"],
                "sp": self.rows[ticket]["sprint"],
                "x": info["external"],
                "d": [d for d in info["deps"] if d not in self.done],
                "a": sorted(self.areas[ticket]),
            }
            if ticket in self.field:
                row["fd"] = [info["field"]["after"], info["field"]["start"], info["field"]["end"]]
            else:
                row["c"] = int(ticket in self.critical)
                row["l"] = self.wave[ticket]
                row["s"] = {n: round(r["start"][ticket], 2) for n, r in self.runs.items()}
                row["f"] = {n: round(r["end"][ticket], 2) for n, r in self.runs.items()}
            rows.append(row)
        scenarios = {
            name: {
                "name": SCENARIO_NAMES[name],
                "K": lanes,
                "hf": factor,
                "end": round(self.end(name), 2),
                "date": self.date(self.end(name)),
                "busy": round(self.busy(name), 2),
            }
            for name, lanes, factor in self.graph["lanes"]
        }
        return {
            "cal": self.calendar,
            "hday": self.per_day,
            "crit": self.critical,
            "sc": scenarios,
            "t": rows,
            "agent": self.agent,
            "ext": self.graph["external_items"],
            "groups": GROUP_TITLES,
            "phases": PHASES,
            "asOf": self.as_of.isoformat(),
        }

    def numbers(self) -> Dict[str, str]:
        """Return the figures the page text quotes."""
        k4, serial = self.end("k4") / self.per_day, self.end("serial") / self.per_day
        per_day_k4 = len(self.soft) * self.tokens / (self.end("k4") / self.per_day)
        per_day_serial = len(self.soft) * self.tokens / (self.end("serial") / self.per_day)
        return {
            "__TOTAL__": str(len(self.graph["tickets"])),
            "__MERGED__": str(len(self.done)),
            "__AS_OF__": human_date(self.as_of.isoformat(), True),
            "__SOFT__": str(len(self.soft)),
            "__FIELD_N__": str(len(self.field)),
            "__CRIT_N__": str(len(self.critical)),
            "__CRIT_H__": f"{self.rank[self.critical[0]]:.0f}",
            "__EXT_N__": str(sum(1 for t in self.soft if self.graph["tickets"][t]["external"])),
            "__WEEKS_K4__": f"{k4 / 5:.0f}",
            "__WEEKS_SERIAL__": f"{serial / 5:.0f}",
            "__K6_LOCK__": f"{self.end('k6_light') / self.per_day:.0f}",
            "__K4_DAYS__": f"{k4:.0f}",
            "__K6_NOLOCK__": f"{max(self.unlocked['end'].values()) / self.per_day:.0f}",
            "__K4_BUSY__": f"{self.busy('k4') * 100:.0f}",
            "__K4_HOURS__": f"{self.busy('k4') * self.per_day:.0f}",
            "__K4L_DAYS__": f"{self.end('k4_light') / self.per_day:.0f}",
            "__TOKENS__": f"{self.tokens:.0f}",
            "__TOK_K4__": f"{per_day_k4:.0f}",
            "__TOK_SERIAL__": f"{per_day_serial:.0f}",
            "__LINKS__": str(sum(len(v["deps"]) for v in self.graph["tickets"].values())),
            "__AGENT_MIN__": f"{self.agent_minutes:.0f}",
            "__M_MIN__": f"{self.agent['M'] * 60:.0f}",
        }

    def html(self) -> str:
        text = TEMPLATE.read_text(encoding="utf-8")
        for token, value in self.numbers().items():
            text = text.replace(token, value)
        return text.replace("__DATA__", json.dumps(self.data(), ensure_ascii=False, separators=(",", ":")))

    def markdown(self) -> str:
        """Return the generated part of the roadmap page."""
        n = self.numbers()
        out = [
            START,
            "",
            '## <a id="timeline"></a>📆 Timeline',
            "",
            (
                f"As of {n['__AS_OF__']}: {n['__MERGED__']} of the {n['__TOTAL__']} tickets are merged. The "
                f"{n['__SOFT__']} software tickets left are scheduled in working days of {self.per_day:.0f} hours, "
                "without holidays. The [interactive Gantt chart](gantt/parallel-plan.html) shows every ticket."
            ),
            "",
            "| Scenario | Lanes | Review time | Working days | Built by | Review load |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for name, lanes, factor in self.graph["lanes"]:
            review = "full" if factor == 1 else "halved off identity and isolation"
            out.append(
                f"| {SCENARIO_NAMES[name]} | {lanes} | {review} | {self.end(name) / self.per_day:.0f} | "
                f"{human_date(self.date(self.end(name)), True)} | {self.busy(name) * 100:.0f} % |"
            )
        out += [
            "| Roadmap plan, 5 tickets per sprint | | | 24 months | 29 Dec 2028 | |",
            "",
            "```mermaid",
            "gantt",
            "    title Building the software tickets, by scenario",
            "    dateFormat YYYY-MM-DD",
            "    axisFormat %d %b",
        ]
        for name, _, _ in self.graph["lanes"]:
            out.append(
                f"    {SCENARIO_NAMES[name].replace(',', '')} :{name}, {self.as_of.isoformat()}, "
                f"{self.date(self.end(name))}"
            )
        out += [
            "```",
            "",
            "With 4 tickets at once, every phase overlaps the others:",
            "",
            "```mermaid",
            "gantt",
            "    title Phases, 4 tickets at once",
            "    dateFormat YYYY-MM-DD",
            "    axisFormat %d %b",
        ]
        run = self.runs["k4"]
        for phase, title in enumerate(PHASES):
            mine = [t for t in self.soft if self.rows[t]["phase"] == str(phase)]
            first, last = min(run["start"][t] for t in mine), max(run["end"][t] for t in mine)
            out.append(f"    {title} ({len(mine)}) :p{phase}, {self.date(first)}, {self.date(last)}")
        out += [
            "```",
            "",
            '## <a id="dependencies"></a>⛓️ Dependencies',
            "",
            "**Ready now**, every ticket they need merged:",
            "",
        ]
        out += [f"- {t}: {self.rows[t]['title']}" for t in sorted(self.soft, key=key) if self.wave[t] == 1]
        out += [
            "",
            (
                f"**Critical path**, {n['__CRIT_N__']} tickets and {n['__CRIT_H__']} hours of work: the floor, "
                "whatever the number of lanes."
            ),
            "",
            " › ".join(self.critical),
            "",
            (
                "**Waves**: a ticket's wave is one more than the latest wave of the tickets it needs. Tickets of a "
                "wave can run together when they share no area."
            ),
            "",
            "| Wave | Tickets | Count |",
            "| --- | --- | --- |",
        ]
        for wave in range(1, max(self.wave.values()) + 1):
            mine = [t for t in sorted(self.soft, key=key) if self.wave[t] == wave]
            out.append(f"| {wave} | {' '.join(mine)} | {len(mine)} |")
        out += [
            "",
            '## <a id="field"></a>🛫 Field validation',
            "",
            (
                f"{n['__EXT_N__']} software tickets are built and tested on the Simulator first, but their "
                f"acceptance waits for an external item. {n['__FIELD_N__']} more only exist after a campaign or the "
                "Patrol beta. These keep the dates of the roadmap: parallel work does not move them."
            ),
            "",
            "```mermaid",
            "gantt",
            "    title Field validation",
            "    dateFormat YYYY-MM-DD",
            "    axisFormat %b %Y",
            "    section Software",
            f"    {n['__SOFT__']} tickets, 4 at once :sw, {self.as_of.isoformat()}, {self.date(self.end('k4'))}",
        ]
        for group, items in self.graph["external_items"].items():
            out.append(f"    section {GROUP_TITLES[group][2:].strip()}")
            for item in items:
                label = f"{item[0]} {item[2]}".replace(",", "")
                if len(item) > 4:
                    out.append(f"    {label} :{item[0].lower()}, {item[1]}, {item[4]}")
                else:
                    out.append(f"    {label} :milestone, {item[0].lower()}, {item[1]}, 0d")
        out += ["```", "", "| Item | Date | Tickets waiting for it | Tickets after it |", "| --- | --- | --- | --- |"]
        tickets = self.graph["tickets"]
        for group, items in self.graph["external_items"].items():
            for item in items:
                waiting = self.waiting_on(item[0])
                after = [t for t in self.field if tickets[t]["field"]["after"] == item[0]]
                if waiting or after:
                    icon = GROUP_TITLES[group].split()[0]
                    out.append(
                        f"| [{icon} {item[0]}]({item[3]}) {item[2]} | {human_date(item[1], True)} | "
                        f"{' '.join(waiting) or '➖'} | {' '.join(after) or '➖'} |"
                    )
        return "\n".join(out + ["", END])


def human_date(iso: str, year: bool = False) -> str:
    y, m, d = (int(part) for part in iso.split("-"))
    return f"{d} {MONTHS[m - 1]}" + (f" {y}" if year else "")


def with_block(page: str, block: str) -> str:
    start, end = page.index(START), page.index(END) + len(END)
    return page[:start] + block + page[end:]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=USAGE.splitlines()[0])
    parser.add_argument("command", choices=["build", "check"])
    args = parser.parse_args(argv)
    plan = Plan()
    page = PAGE.read_text(encoding="utf-8")
    outputs = {HTML: plan.html(), PAGE: with_block(page, plan.markdown())}
    if args.command == "build":
        for path, text in outputs.items():
            path.write_text(text, encoding="utf-8")
        return 0
    stale = [path for path, text in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != text]
    for path in stale:
        print(f"{path.relative_to(ROOT)}: out of date, run python3 .claude/scripts/reports/roadmap_gantt.py build")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
