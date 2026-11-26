## Review: T0.15 Four languages (round 2, confirm fixes)

**Verdict:** approve. No blocking finding is left.

### What changed since round 1
- The `➖ No screen` reason in `TICKET.md` (Screens touched) and in `PLAN.md` (Assumptions) is now true. The four shells are the empty frames of T0.14 and show no use case state. The ticket only translates their side bar items, Hold, Abort and the status bar language into the four languages.
- `PROGRESS.md` records that this was fixed by hand. The fix tasks K18 and K20 own neither file.
- The clean-tree check outputs are now in `tests-evidences/`.

### Acceptance criteria
1. A message in English only makes CI fail. Evidence: `tests-evidences/test.txt`, `pytest.txt` (4548 passed, 79 skipped). Result: pass, as in round 1.
2. The shells switch language without reloading. Evidence: `tests-evidences/test.txt` (Vitest in the four shells), `typecheck.txt`, `lint.txt`. Result: pass, as in round 1.
3. A Client who chose German gets German: here, the stored language and its use at sign-in. Evidence: `tests-evidences/pytest.txt` (swarm-models Person tests). Result: pass, as in round 1.

`ticket-refs.txt` and `specs-check.txt` print nothing.

### What to look at first
- `docs/tickets/T0.15/TICKET.md` line 33: the new No screen reason. It matches the frame diff in `packages/ts/ui/src/frames/SideBar.tsx`, where Hold and Abort now come from `action.hold` and `action.abort` through `intl.formatMessage`. Only labels change, and no use case state is added.
- The fix round touched only documents and evidence. No code, identity, Operator isolation or Simulator isolation change was added.

### Assumptions accepted
- No screen is captured. The shells show no use case state, only translated labels, and T0.20 is not merged, so TKT-21 capture does not apply yet.

### Follow-ups
- `TICKET.md` line 47 (Assumptions) still gives the old no-screen reason ("the roadmap row names no use case"). Align it with the new Screens touched line.
