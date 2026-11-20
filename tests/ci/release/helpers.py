from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Union, cast

import yaml
from pydantic import JsonValue

REPO = "gpbcom/swarm"
HEAD_SHA = "a" * 40
MERGE_SHA = "b" * 40
GITHUB_TOKEN = "github-token"
RELEASE_TOKEN = "release-token"
FAKE_GH = r'''#!/usr/bin/env python3
"""A stand-in for gh: answers from scenario.json, applies --jq with jq, and logs every call."""
import json, os, subprocess, sys
from pathlib import Path

here = Path(__file__).resolve().parent
scenario = json.loads((here / "scenario.json").read_text())
args = sys.argv[1:]
with (here / "calls.jsonl").open("a") as log:
    log.write(json.dumps({"argv": args, "token": os.environ.get("GH_TOKEN", "")}) + "\n")
query = args[args.index("--jq") + 1] if "--jq" in args else None
text = " ".join(args)

def answer(value):
    if query is None:
        print(value if isinstance(value, str) else json.dumps(value))
        return
    out = subprocess.run(["jq", "-r", query], input=json.dumps(value), capture_output=True, text=True, env=os.environ)
    sys.stdout.write(out.stdout)
    sys.exit(out.returncode)

if args[:2] == ["pr", "list"]:
    answer(scenario["open_after"] if "--json number" in text and "baseRefName" not in text else scenario["prs"])
elif "check-runs" in text:
    answer({"check_runs": [{"name": n, "conclusion": c} for n, c in scenario["checks"].items()]})
elif "/files" in text:
    answer([{"filename": f} for f in scenario["files"]])
elif text.startswith("api repos/") and "/labels" in text and "-X" not in args:
    answer([{"name": n} for n in scenario.get("labels", [])])
elif "git/ref/heads/" in text and "-X" not in args:
    if scenario.get("branch_gone"):
        print("gh: Not Found (HTTP 404)", file=sys.stderr)
        sys.exit(1)
    answer({"object": {"sha": scenario["ref_sha"]}})
elif "/contents/" in text:
    answer("# Swarm notes from the repository")
elif args[:2] == ["pr", "view"]:
    answer({"mergeCommit": {"oid": scenario["merge_sha"]}, "title": scenario["title"]})
'''


def workflow(name: str) -> Dict[Union[str, bool], JsonValue]:
    path = Path(__file__).resolve().parents[3] / ".github" / "workflows" / name
    return cast(Dict[Union[str, bool], JsonValue], yaml.safe_load(path.read_text(encoding="utf-8")))


def steps(name: str, job: str) -> List[Dict[str, JsonValue]]:
    jobs = cast(Dict[str, Dict[str, JsonValue]], workflow(name)["jobs"])
    return cast(List[Dict[str, JsonValue]], jobs[job]["steps"])


def runs(name: str, job: str) -> str:
    return "\n".join(str(step.get("run", "")) for step in steps(name, job))


def scenario(
    head: str,
    base: str,
    files: List[str],
    checks: Dict[str, str],
    ref_sha: str = HEAD_SHA,
    title: str = "T0.10: Dev cell observability",
) -> Dict[str, JsonValue]:
    pull_request = {"number": 12, "baseRefName": base, "headRefOid": HEAD_SHA, "labels": [{"name": "automerge"}]}
    return {
        "head": head,
        "prs": [pull_request],
        "checks": checks,
        "files": files,
        "ref_sha": ref_sha,
        "merge_sha": MERGE_SHA,
        "title": title,
        "open_after": [],
    }


def run_automerge(
    tmp_path: Path, case: Dict[str, JsonValue], release_token: str = RELEASE_TOKEN
) -> List[Dict[str, JsonValue]]:
    """Run the merge step of automerge.yml with bash and the fake gh, and return the gh calls it made."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH, encoding="utf-8")
    gh.chmod(0o755)
    (bin_dir / "scenario.json").write_text(json.dumps(case), encoding="utf-8")
    env = {
        **os.environ,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "GH_TOKEN": GITHUB_TOKEN,
        "RELEASE_TOKEN": release_token,
        "REPO": REPO,
        "HEAD_BRANCH": str(case["head"]),
        "HEAD_SHA": HEAD_SHA,
        "RUNNER_TEMP": str(tmp_path),
    }
    result = subprocess.run(
        ["bash", "-e", "-c", runs("automerge.yml", "merge")], env=env, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    log = bin_dir / "calls.jsonl"
    lines = log.read_text(encoding="utf-8").splitlines() if log.is_file() else []
    return [cast(Dict[str, JsonValue], json.loads(line)) for line in lines]


def calls_to(calls: List[Dict[str, JsonValue]], *words: str) -> List[Dict[str, JsonValue]]:
    """Return the gh calls whose arguments start with ``words``."""
    return [call for call in calls if cast(List[str], call["argv"])[: len(words)] == list(words)]


def argv(call: Dict[str, JsonValue]) -> str:
    return " ".join(cast(List[str], call["argv"]))
