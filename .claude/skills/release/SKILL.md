---
name: release
description: Release Swarm - start the release workflow on develop, which runs every test suite, writes the changelog, the release notes and the test reports on release/<version>, and lets automerge merge it into master, tag it, publish it and bring it back to develop, with no commit or merge by hand (TKT-26). Use when the person types /release, optionally with a version such as /release 1.0.0, or asks to release or to bring master up to date.
---

# Release

A release reaches `master` by itself (TKT-26, `.claude/rules/tickets.md`). This skill starts it and follows it.

1. Check `gh secret list -R gpbcom/swarm` lists `RELEASE_TOKEN`. If it does not, stop and give the person the README
   section "🚢 Releases": the token is theirs to create.
2. Say what will be released: `git fetch -q origin`, the last tag (`git tag --list 'v*' --sort=-v:refname | head -1`)
   and `git log --oneline --first-parent <last tag or origin/master>..origin/develop | wc -l` pull requests.
3. Start it (the PreToolUse hook asks the person first):
   `gh workflow run release.yml -R gpbcom/swarm --ref develop` and `-f version=<x.y.z>` when the person gave one.
4. Follow it: find the run with `gh run list -R gpbcom/swarm --workflow release.yml --limit 1`, then watch it in the
   background (`gh run watch <id> -R gpbcom/swarm --exit-status`). When it ends, report each job with ✅ or ❌.
5. Then follow the pull request `Release v<version>` to `master` and its way back to `develop` (`gh pr list -R
   gpbcom/swarm --state all --head release/<version>`) until both are merged, and give the person the GitHub release
   (`gh release view v<version> -R gpbcom/swarm --json url`), the changelog and the test report verdict.

Never commit, merge, tag or push anything by hand for a release: when a step fails, report the failing job with its
log and stop.
