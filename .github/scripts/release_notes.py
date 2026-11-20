from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import List, Optional, Sequence, Tuple
from xml.etree import ElementTree

USAGE = """Write what a release delivers to master: changelog, release notes and test reports (TKT-26).

Usage:
    python3 .github/scripts/release_notes.py version [--requested <x.y.z>] [--root <repo root>]
    python3 .github/scripts/release_notes.py write --version <x.y.z> --reports <dir> [--root <repo root>]
        [--date <yyyy-mm-dd>]

``version`` prints ``version=<x.y.z>``: the requested one, or the next minor version after the last ``v*`` tag
(``0.1.0`` when there is none). It exits 1 when the tag already exists and 2 on a malformed version.

``write`` compares ``HEAD`` with the previous release (the last ``v*`` tag, else ``origin/master``, else the first
commit) and writes, from the repository and the CI test reports only:

- ``CHANGELOG.md``: a new section on top, one line per commit of each pull request merged since, grouped by kind;
- ``docs/releases/v<x.y.z>/RELEASE_NOTES.md``: the tickets delivered (with their FS, UC and BR), the test summary, the
  changes by kind;
- ``docs/releases/v<x.y.z>/TEST_REPORT.md``: one row per test suite (passed, failed, skipped, time) and the overall
  verdict, from the JUnit XML and the logs that CI uploads as ``test-report-*`` artifacts;
- ``docs/releases/v<x.y.z>/tests/``: those raw reports.

It exits 1, writing nothing, when ``--reports`` holds no report: a release never reaches master without its tests.
"""

VERSION = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
TICKET = re.compile(r"^(T\d+\.\d{2})[: ]")
PULL_REQUEST = re.compile(r"\(#(\d+)\)\s*$")
SPEC_LINK = re.compile(r"\[((?:📘 FS|🎬 UC|📏 BR)-\d{3}: [^\]]+)\]")
RUST_RESULT = re.compile(r"test result: \w+\. (\d+) passed; (\d+) failed; (\d+) ignored")
VITEST_RESULT = re.compile(r"Tests\s+(?:(\d+) failed \| )?(\d+) passed(?: \| (\d+) skipped)?")
TAP_COUNT = re.compile(r"^# (pass|fail|skipped|todo) (\d+)$", re.MULTILINE)
MERGE_PREFIX = re.compile(r"^(?P<kind>[^:]+): merge (?P<branch>\S+) into develop")
GROUPS: List[Tuple[str, str]] = [
    ("ticket", "🎫 Tickets"),
    ("harness", "🧰 Harness"),
    ("specs", "📐 Specifications"),
    ("ci", "🚦 CI/CD and fixes"),
    ("other", "📦 Other changes"),
]
KIND_OF_PREFIX = {"harness": "harness", "board": "harness", "specs": "specs", "ci": "ci", "fix": "ci", "release": "ci"}
CHANGELOG = "CHANGELOG.md"
CHANGELOG_HEADER = (
    "# 📜 Changelog\n\nEvery release of Swarm, newest first: one line per commit of each pull request merged into "
    "`develop`, written by the release workflow (TKT-26).\n"
)
RELEASES = Path("docs/releases")
REMOTE_MASTER = "origin/master"
USAGE_EXIT = 2
SPECS_CLEAN = "specs.py check printed nothing."


@dataclass
class Change:
    """One commit of the release, with the pull request that brought it."""

    subject: str
    kind: str
    pull_request: Optional[int]


@dataclass
class Suite:
    """The result of one test suite."""

    name: str
    report: str
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    seconds: float = 0.0
    notes: List[str] = field(default_factory=list)


###############
# Git reading #
###############


def git(root: Path, *args: str) -> str:
    """Run git in ``root`` and return its output, raising ``RuntimeError`` on failure."""
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def tags(root: Path) -> List[str]:
    """Return the release tags, newest version first."""
    return [tag for tag in git(root, "tag", "--list", "v*", "--sort=-v:refname").splitlines() if VERSION.match(tag)]


def next_version(root: Path, requested: str) -> str:
    """Return the version to release: the requested one, or the next minor after the last tag."""
    if requested:
        match = VERSION.match(requested.strip())
        if not match:
            raise ValueError(f"Invalid version: {requested!r}. Must be x.y.z.")
        return ".".join(match.groups())
    existing = tags(root)
    if not existing:
        return "0.1.0"
    major, minor, _ = (int(part) for part in VERSION.match(existing[0]).groups())  # type: ignore[union-attr]
    return f"{major}.{minor + 1}.0"


def previous_release(root: Path) -> Optional[str]:
    """Return the commit the release starts after: the last tag, else ``origin/master``, else none."""
    existing = tags(root)
    if existing:
        return existing[0]
    try:
        return git(root, "rev-parse", "--verify", "--quiet", REMOTE_MASTER)
    except RuntimeError:
        return None


def kind_of(subject: str, merge_kind: str) -> str:
    """Return the group of a commit, from its subject or the prefix of its merge."""
    if TICKET.match(subject) or TICKET.match(merge_kind + " "):
        return "ticket"
    for word in (subject.split(":", 1)[0], merge_kind):
        found = KIND_OF_PREFIX.get(word.strip().lower())
        if found:
            return found
    return "other"


def changes(root: Path, since: Optional[str]) -> List[Change]:
    """Return every commit merged into ``HEAD`` since ``since``, through its pull request when it had one."""
    span = f"{since}..HEAD" if since else "HEAD"
    found: List[Change] = []
    for line in git(root, "log", "--first-parent", "--format=%H %P%x09%s", span).splitlines():
        hashes, subject = line.split("\t", 1)
        commit, *parents = hashes.split()
        number = PULL_REQUEST.search(subject)
        pull_request = int(number.group(1)) if number else None
        merge = MERGE_PREFIX.match(subject)
        if len(parents) < 2:
            found.append(Change(subject, kind_of(subject, ""), pull_request))
            continue
        merge_kind = merge.group("kind") if merge else ""
        inner = git(root, "log", "--no-merges", "--reverse", "--format=%s", f"{parents[0]}..{commit}").splitlines()
        for text in inner or [subject]:
            found.append(Change(text, kind_of(text, merge_kind), pull_request))
    return found


def delivered_tickets(root: Path, since: Optional[str]) -> List[Tuple[str, str, List[str]]]:
    """Return the tickets whose ``EXPLAIN.md`` arrived since ``since``: ID, title, features, use cases and rules."""
    now = set(git(root, "ls-tree", "-r", "--name-only", "HEAD", "docs/tickets").splitlines())
    before = set(git(root, "ls-tree", "-r", "--name-only", since, "docs/tickets").splitlines()) if since else set()
    found: List[Tuple[str, str, List[str]]] = []
    for name in sorted(now - before):
        parts = name.split("/")
        if len(parts) != 4 or parts[3] != "EXPLAIN.md":
            continue
        ticket = parts[2]
        text = (root / "docs" / "tickets" / ticket / "TICKET.md").read_text(encoding="utf-8")
        title = next((line[2:].split(":", 1)[-1].strip() for line in text.splitlines() if line.startswith("# ")), "")
        found.append((ticket, title, list(dict.fromkeys(SPEC_LINK.findall(text)))))
    return found


################
# Test reports #
################


def junit_suite(path: Path, name: str) -> Suite:
    """Read one JUnit XML report (pytest's): totals of its test suites."""
    suite = Suite(name, path.name)
    root = ElementTree.parse(path).getroot()
    for node in [root] if root.tag == "testsuite" else root.iter("testsuite"):
        tests = int(node.get("tests", 0))
        failed = int(node.get("failures", 0)) + int(node.get("errors", 0))
        skipped = int(node.get("skipped", 0))
        suite.failed += failed
        suite.skipped += skipped
        suite.passed += tests - failed - skipped
        suite.seconds += float(node.get("time", 0.0))
    return suite


def log_suite(path: Path, name: str) -> Suite:
    """Read a test log: cargo test, Vitest, Node's test runner (TAP), or the output of ``specs.py check``."""
    suite = Suite(name, path.name)
    text = path.read_text(encoding="utf-8", errors="replace")
    for passed, failed, ignored in RUST_RESULT.findall(text):
        suite.passed += int(passed)
        suite.failed += int(failed)
        suite.skipped += int(ignored)
    for failed, passed, skipped in VITEST_RESULT.findall(text):
        suite.passed += int(passed)
        suite.failed += int(failed or 0)
        suite.skipped += int(skipped or 0)
    for kind, count in TAP_COUNT.findall(text):
        if kind == "pass":
            suite.passed += int(count)
        elif kind == "fail":
            suite.failed += int(count)
        else:
            suite.skipped += int(count)
    if name.startswith("specs"):
        if text.strip() and text.strip() != SPECS_CLEAN:
            suite.failed += 1
            suite.notes.append("specs.py check printed problems")
        else:
            suite.passed += 1
            suite.notes.append("specs.py check printed nothing")
    elif suite.passed + suite.failed + suite.skipped == 0:
        suite.notes.append("no test ran")
    return suite


def read_reports(reports: Path) -> List[Suite]:
    """Return one suite per report file under ``reports`` (one folder per CI artifact)."""
    suites: List[Suite] = []
    for path in sorted(p for p in reports.rglob("*") if p.is_file()):
        relative = path.relative_to(reports)
        name = "/".join(relative.with_suffix("").parts).removeprefix("test-report-")
        if path.suffix == ".xml":
            suite = junit_suite(path, name)
        elif path.suffix == ".log":
            suite = log_suite(path, name)
        else:
            continue
        suite.report = relative.as_posix()
        suites.append(suite)
    return suites


#############
# Rendering #
#############


def change_line(change: Change) -> str:
    suffix = (
        f" (#{change.pull_request})"
        if change.pull_request and f"(#{change.pull_request})" not in change.subject
        else ""
    )
    return f"- {change.subject}{suffix}"


def changelog_section(version: str, day: str, found: List[Change]) -> str:
    lines = [f"## [v{version}]({RELEASES.as_posix()}/v{version}/RELEASE_NOTES.md) - {day}", ""]
    for kind, title in GROUPS:
        group = [change for change in found if change.kind == kind]
        if group:
            lines += [f"### {title}", "", *[change_line(change) for change in group], ""]
    if not found:
        lines += ["No change since the previous release.", ""]
    return "\n".join(lines)


def write_changelog(root: Path, section: str) -> None:
    path = root / CHANGELOG
    old = path.read_text(encoding="utf-8") if path.is_file() else CHANGELOG_HEADER
    head, _, rest = old.partition("\n## ")
    body = f"## {rest}" if rest else ""
    path.write_text(f"{head.rstrip()}\n\n{section.rstrip()}\n\n{body}".rstrip() + "\n", encoding="utf-8")


def test_table(suites: List[Suite]) -> List[str]:
    lines = ["| Suite | ✅ Passed | ❌ Failed | ⏭️ Skipped | ⏱️ Time | Report |", "| --- | --- | --- | --- | --- | --- |"]
    for suite in suites:
        icon = "❌" if suite.failed else ("➖" if suite.passed + suite.skipped == 0 else "✅")
        notes = f" ({'; '.join(suite.notes)})" if suite.notes else ""
        lines.append(
            f"| {icon} {suite.name}{notes} | {suite.passed} | {suite.failed} | {suite.skipped} | "
            f"{suite.seconds:.1f} s | [{Path(suite.report).name}](tests/{suite.report}) |"
        )
    return lines


def totals(suites: List[Suite]) -> Tuple[int, int, int]:
    return sum(s.passed for s in suites), sum(s.failed for s in suites), sum(s.skipped for s in suites)


def test_report(version: str, commit: str, suites: List[Suite]) -> str:
    passed, failed, skipped = totals(suites)
    verdict = f"❌ {failed} failed" if failed else "✅ Every test passed"
    return "\n".join(
        [
            f"# 🧪 Test report: Swarm v{version}",
            "",
            (
                f"**Commit:** `{commit}` · **Verdict:** {verdict} · ✅ {passed} passed · ❌ {failed} failed · "
                f"⏭️ {skipped} skipped"
            ),
            "",
            (
                "Every suite of CI, run on the released commit with every service, package and front end selected. "
                "The raw reports are in [tests/](tests/)."
            ),
            "",
            *test_table(suites),
            "",
        ]
    )


def release_notes(
    version: str,
    day: str,
    commit: str,
    since: Optional[str],
    tickets: List[Tuple[str, str, List[str]]],
    found: List[Change],
    suites: List[Suite],
) -> str:
    passed, failed, skipped = totals(suites)
    lines = [
        f"# 🚀 Swarm v{version}",
        "",
        f"**Released:** {day} · **Commit:** `{commit}` · **Since:** `{since or 'the first commit'}`",
        "",
        (
            f"> [!NOTE]\n> {len(tickets)} ticket(s) delivered, {len(found)} change(s), "
            f"tests: ✅ {passed} passed, ❌ {failed} failed, ⏭️ {skipped} skipped."
        ),
        "",
        "## 🎫 Tickets delivered",
        "",
    ]
    if tickets:
        lines += ["| Ticket | Title | Features, use cases and business rules |", "| --- | --- | --- |"]
        for ticket, title, features in tickets:
            link = f"[{ticket}](../../tickets/{ticket}/EXPLAIN.md)"
            lines.append(f"| {link} | {title} | {'<br>'.join(features) or '➖'} |")
    else:
        lines.append("No roadmap ticket was finished in this release.")
    lines += ["", "## 🧪 Tests", "", "[🧪 Full test report](TEST_REPORT.md)", "", *test_table(suites), ""]
    lines += ["## 📜 Changes", "", f"The [changelog](../../../{CHANGELOG}) lists every commit. By kind:", ""]
    for kind, title in GROUPS:
        count = len([change for change in found if change.kind == kind])
        if count:
            lines.append(f"- {title}: {count}")
    return "\n".join(lines).rstrip() + "\n"


############
# Commands #
############


def write(root: Path, version: str, reports: Path, day: str) -> int:
    suites = read_reports(reports) if reports.is_dir() else []
    if not suites:
        print(f"No test report in {reports}: a release never reaches master without its tests.", file=sys.stderr)
        return 1
    since = previous_release(root)
    commit = git(root, "rev-parse", "HEAD")
    found = changes(root, since)
    folder = root / RELEASES / f"v{version}"
    if folder.exists():
        shutil.rmtree(folder)
    shutil.copytree(reports, folder / "tests")
    tickets = delivered_tickets(root, since)
    (folder / "TEST_REPORT.md").write_text(test_report(version, commit, suites), encoding="utf-8")
    notes = release_notes(version, day, commit, since, tickets, found, suites)
    (folder / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8")
    write_changelog(root, changelog_section(version, day, found))
    print(f"v{version}: {len(found)} changes, {len(tickets)} tickets, {len(suites)} test suites, written to {folder}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=USAGE.splitlines()[0] if USAGE else None)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)
    pick = sub.add_parser("version")
    pick.add_argument("--requested", default="")
    out = sub.add_parser("write")
    out.add_argument("--version", required=True)
    out.add_argument("--reports", type=Path, required=True)
    out.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        version = next_version(root, args.requested if args.command == "version" else args.version)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return USAGE_EXIT
    if args.command == "version":
        if f"v{version}" in tags(root):
            print(f"v{version} is already released: ask for another version.", file=sys.stderr)
            return 1
        print(f"version={version}")
        return 0
    return write(root, version, args.reports.resolve(), args.date)


if __name__ == "__main__":
    sys.exit(main())
