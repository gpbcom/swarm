export const meta = {
  name: 'ticket-run',
  description: 'Run an approved ticket plan in the main checkout, on the branch feature/tickets shared by every running ticket: parallel waves handed off uncommitted, integration, verification, review, EXPLAIN.md and IMPLEMENTATION.md, then stop for the person to review the code; once they approve the push, one commit pushed with its pull request to develop, merged by GitHub once CI passes',
  whenToUse: 'After the person approved docs/tickets/<ID>/PLAN.md, for example /ticket-run T1.07, or /ticket-run T1.07 --force to start despite the start rule (TKT rules in .claude/rules/tickets.md). Run it again after setting "**Push:** 🟢 Approved" in PLAN.md to push the reviewed code (TKT-18). Several tickets may run at once (TKT-16)',
  phases: [
    { title: 'Gate', detail: 'refuse unless PLAN.md is approved and the start rule holds; put the main checkout on feature/tickets' },
    { title: 'Waves', detail: 'workers in their own worktrees, at most 8 at once, hand off uncommitted; integrator applies each wave' },
    { title: 'Verify', detail: 'verifier runs every check; owners fix failures, at most twice' },
    { title: 'Review', detail: 'reviewer gates the diff; owners fix findings, at most twice' },
    { title: 'Finish', detail: 'EXPLAIN.md, IMPLEMENTATION.md, REVIEW.md, PROGRESS.md, then stop for the person to review the code; once approved, the single commit pushed with its pull request' },
  ],
}

const RAW = String(typeof args === 'string' ? args : (args && args.ticket) || '').trim()
const ID = RAW.split(/\s+/)[0]
// TKT-16: --force starts the ticket although the start rule finds a problem (the person decides, and it is logged).
const FORCE = /(^|\s)--force(\s|$)/.test(RAW) || Boolean(args && typeof args === 'object' && args.force)
if (!/^T\d\.\d{2}$/.test(ID)) throw new Error('Usage: /ticket-run T1.07 [--force] (a ticket ID of the roadmap)')
const MAX_PARALLEL = 8
const MAX_FIX_ROUNDS = 2

const TASK = {
  type: 'object',
  properties: {
    id: { type: 'string' }, title: { type: 'string' }, agent: { type: 'string' },
    depends_on: { type: 'array', items: { type: 'string' } }, files: { type: 'array', items: { type: 'string' } },
    wave: { type: 'integer' },
  },
  required: ['id', 'title', 'agent', 'depends_on', 'files', 'wave'],
}
const GATE = {
  type: 'object',
  properties: {
    approved: { type: 'boolean' }, status: { type: 'string' }, tasks: { type: 'array', items: TASK },
    done_tasks: { type: 'array', items: { type: 'string' } },
    push_approved: { type: 'boolean' }, push_status: { type: 'string' },
  },
  required: ['approved', 'status', 'tasks', 'done_tasks', 'push_approved'],
}
// TKT-18: the person reviews the code before anything is committed or pushed. The run that finishes the work stops with
// this line in PLAN.md, under the plan's status line; the person changes it to PUSH_APPROVED and runs /ticket-run again.
const PUSH_AWAITING = '**Push:** 🟡 Awaiting code review'
const PUSH_APPROVED = '**Push:** 🟢 Approved'
// TKT-10: the timings are written by the main checkout's progress.py, which finds every run's transcripts and writes
// into the ticket's home (the main checkout, or the worktree of a ticket started before TKT-16).
const TIMINGS = `python3 "$(git worktree list --porcelain | sed -n '1s/^worktree //p')/.claude/scripts/reports/progress.py" timings --ticket ${ID} --write`
// TKT-14: an implementation choice where a reasonable alternative existed, for IMPLEMENTATION.md.
const DECISION = {
  type: 'object',
  properties: {
    choice: { type: 'string' }, alternatives: { type: 'array', items: { type: 'string' } },
    trade_off: { type: 'string' }, where: { type: 'string' },
  },
  required: ['choice', 'alternatives', 'trade_off', 'where'],
}
// TKT-5: workers never commit; they hand their changes off with ticket_tree.py handoff.
const RESULT = {
  type: 'object',
  properties: {
    status: { type: 'string', enum: ['done', 'blocked', 'failed'] },
    worktree: { type: 'string' },
    files_changed: { type: 'array', items: { type: 'string' } },
    checks: { type: 'array', items: { type: 'string' } },
    assumptions: { type: 'array', items: { type: 'string' } },
    decisions: { type: 'array', items: DECISION },
    note: { type: 'string' },
    // TKT-19: the files of other tasks (most often a test of wave 1) that are wrong and stop this task.
    blocked_by: {
      type: 'array',
      items: { type: 'object', properties: { file: { type: 'string' }, problem: { type: 'string' } }, required: ['file', 'problem'] },
    },
  },
  required: ['status', 'worktree', 'files_changed', 'checks', 'assumptions', 'decisions'],
}
const MERGE = {
  type: 'object',
  properties: {
    integrated: { type: 'array', items: { type: 'string' } },
    conflicts_resolved: { type: 'array', items: { type: 'string' } },
    blocked: { type: 'array', items: { type: 'string' } },
    tree: { type: 'string' },
    home: { type: 'string' },
    pull_request: { type: 'string' },
  },
  required: ['integrated', 'blocked', 'tree'],
}
const VERDICT = {
  type: 'object',
  properties: {
    passed: { type: 'boolean' },
    failures: {
      type: 'array',
      items: {
        type: 'object',
        properties: { check: { type: 'string' }, file: { type: 'string' }, detail: { type: 'string' }, environment: { type: 'boolean' } },
        required: ['check', 'file', 'detail'],
      },
    },
    not_applicable: { type: 'array', items: { type: 'string' } },
  },
  required: ['passed', 'failures'],
}
const CHECK = {
  type: 'object',
  properties: { passed: { type: 'boolean' }, problems: { type: 'array', items: { type: 'string' } } },
  required: ['passed', 'problems'],
}
const REVIEW = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['approve', 'changes'] },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' }, rule: { type: 'string' }, change: { type: 'string' },
          severity: { type: 'string', enum: ['blocking', 'follow-up'] },
        },
        required: ['file', 'rule', 'change', 'severity'],
      },
    },
    resolved: { type: 'array', items: { type: 'string' } },
    assumptions_accepted: { type: 'array', items: { type: 'string' } },
    note: { type: 'string' },
  },
  required: ['verdict', 'findings', 'assumptions_accepted', 'note'],
}

// Run fn over items with at most n agents at once (TKT-4).
async function limited(items, n, fn) {
  const out = []
  let next = 0
  async function worker() {
    while (next < items.length) {
      const k = next++
      out[k] = await fn(items[k], k)
    }
  }
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, worker))
  return out
}

const progress = []
// TKT-16: every running ticket shares the main checkout (its home) and the branch feature/tickets; each touches only its
// own files and docs/tickets/<ID>/, so that
// several tickets run at once. Every agent but the workers works there.
let HOME = ''
function inHome(text) {
  return HOME
    ? `Work in the main checkout ${HOME} (branch feature/tickets, shared with the other running tickets): run every command from there (cd ${HOME}), ` +
      `and change only this ticket's files and docs/tickets/${ID}/, never another ticket's uncommitted work. ${text}`
    : text
}
// The tree of the integrated, uncommitted work after the last integration (TKT-5): the confirm-fixes review diffs from it.
let currentTree = ''
function note(event, by, result) { progress.push(`| ${event} | ${by} | ${result} |`) }

function workerPrompt(t, extra) {
  return `Ticket ${ID}, task ${t.id}: ${t.title}.\nThe ticket's work lives uncommitted in the main checkout ${HOME || 'on feature/tickets'} (TKT-5, TKT-16), not in yours. ` +
    `First run python3 .claude/scripts/tickets/ticket_tree.py start --ticket ${ID} at the root of your worktree: it moves your worktree to the ticket's commit and copies that work in.\n` +
    `Files you may change: ${t.files.join(', ')}.\n` +
    (!/^K\d{2}$/.test(t.id)
      ? `Brief: ${t.brief}\nDone when: ${t.done_when}\n`
      : `First read your brief and done-when exactly as approved: run python3 .claude/scripts/tickets/plan.py task --ticket ${ID} --id ${t.id} ` +
        `at the root of your worktree. Follow them as your brief.\n`) +
    (extra ? `\n${extra}\n` : '') +
    `If a file you may not change (for example a test written by another task) is wrong and stops you, never work around it ` +
    `(no shim, no skip): hand off what you did, set status to blocked and list each such file in blocked_by with exactly what to change (TKT-19).\n` +
    `Never commit, push or merge. Last, run python3 .claude/scripts/tickets/ticket_tree.py handoff --ticket ${ID} --task ${t.id} ` +
    `(again after any later change), and report your decisions (choice, alternatives, trade-off, file:line) for IMPLEMENTATION.md.`
}

async function runTasks(tasks, phaseName, extra) {
  return limited(tasks, MAX_PARALLEL, t =>
    agent(workerPrompt(t, extra), {
      agentType: t.agent, isolation: 'worktree', schema: RESULT, phase: phaseName, label: `${t.id} ${t.agent}`,
    }).then(r => ({ task: t, result: r })))
}

async function integrate(results, label) {
  const ids = results.filter(r => r.result && r.result.status === 'done').map(r => r.task.id)
  if (!ids.length) return null
  const merge = await agent(inHome(
    `Ticket ${ID}: integrate the hand-offs of these tasks into the main checkout, in this order: ` +
    `python3 .claude/scripts/tickets/ticket_tree.py integrate --ticket ${ID} ${ids.map(id => `--task ${JSON.stringify(id)}`).join(' ')}. ` +
    `Then run the quick checks for what they changed (ruff check, cargo check or tsc as relevant). Commit nothing (TKT-5).`),
    { agentType: 'integrator', schema: MERGE, phase: label, label: `integrator ${label}` },
  )
  note(`Integrate (${label})`, 'integrator', merge ? `✅ ${merge.integrated.length} integrated, ${merge.blocked.length} blocked, not committed` : '❌ failed')
  if (merge && /^[0-9a-f]{7,40}$/.test(merge.tree)) currentTree = merge.tree
  return merge
}

// Fix loop: send each failure or finding to every task that owns one of its files, each fixer only its own problems
const ROOTS = ['services/', 'packages/', 'frontends/', 'tests/', 'deploy/', 'docs/', '.claude/', '.github/']
function normalise(file) {
  let f = String(file || '').trim().replace(/:\d+(-\d+)?$/, '')
  for (const r of ROOTS) {
    const i = f.indexOf('/' + r)
    if (i >= 0) { f = f.slice(i + 1); break }
  }
  if (f.startsWith('/')) f = f.split('/').pop()
  return f
}
function agentFor(f) {
  if (f.startsWith('packages/rust/') || f.endsWith('.rs')) return 'rust-implementer'
  if (f.startsWith('frontends/') || f.startsWith('packages/ts/') || /\.(ts|tsx)$/.test(f)) return 'frontend-implementer'
  if (f.startsWith('tests/')) return 'test-writer'
  if (f.startsWith('docs/') || /\.md$/.test(f)) return 'doc-writer'
  return 'implementer'
}
// The paths named in a finding's file field, which may list several: "a/b.yaml:4 (also :9) and c/d.tpl:3, e/f".
// Bare file names ("service.yaml") are left out: they belong to the path before them, whose owner is already found.
function pathsOf(item) {
  return String(item.file || '').split(/[\s,;()]+/).map(normalise).filter(f => f.includes('/'))
}
// Every task that owns the finding: the owners of each path it names, plus the tasks the reviewer names in its rule
// ("Owners: K21 and K22"). A finding that spans two tasks goes to both, each fixing its own files; sending it to the
// first owner only left the other half unfixed (T0.08). The change text is read for task IDs only when nothing else
// names an owner, because it often mentions other tasks in passing.
function ownersOf(item) {
  const byId = ids => ids.map(id => tasks.find(t => t.id === id)).filter(Boolean)
  const owners = []
  const add = t => { if (t && !owners.includes(t)) owners.push(t) }
  const files = pathsOf(item)
  for (const f of files) {
    const dir = f.replace(/\/$/, '') + '/'
    tasks.filter(t => t.files.some(x => x === f || x.endsWith('/' + f) || f.endsWith('/' + x) || x.startsWith(dir))).forEach(add)
  }
  byId(String(item.check || '').match(/\bK\d{2}\b/g) || []).forEach(add)
  if (!owners.length) byId(String(item.detail || '').match(/\bK\d{2}\b/g) || []).forEach(add)
  if (owners.length) return owners
  const f = files[0] || normalise(item.file) || 'unknown'
  return [{ id: `FIX-${f}`, title: `Fix ${f}`, agent: agentFor(f), files: files.length ? files : [f], brief: '', done_when: 'the verifier passes' }]
}
async function fixRound(items, label) {
  const groups = {}
  for (const it of items) {
    for (const owner of ownersOf(it)) {
      groups[owner.id] = groups[owner.id] || { task: owner, items: [] }
      groups[owner.id].items.push(it)
    }
  }
  log(`${label}: ${items.length} problem(s) sent to ${Object.keys(groups).length} fixer(s): ${Object.keys(groups).join(', ')}`)
  const results = await limited(Object.values(groups), MAX_PARALLEL, g =>
    agent(workerPrompt(g.task, `Fix only these problems, within your files: ${JSON.stringify(g.items)}`), {
      agentType: g.task.agent, isolation: 'worktree', schema: RESULT, phase: label, label: `${g.task.id} ${g.task.agent} (fix)`,
    }).then(r => ({ task: g.task, result: r })))
  collect(results)
  await integrate(results, label)
}

// Gate ---------------------------------------------------------------------------------------------------------
phase('Gate')
const WHERE = `Work in the ticket's home: python3 .claude/scripts/tickets/ticket_tree.py home --ticket ${ID} prints it (the main checkout, or a worktree for a ticket started before TKT-16); run every command from there. `
const gate = await agent(
  WHERE + `Read docs/tickets/${ID}/PLAN.md. approved is true only if its status line is exactly "**Plan:** 🟢 Approved". ` +
  `Return the status line, and in tasks the JSON array printed by python3 .claude/scripts/tickets/plan.py outline --ticket ${ID}, exactly, without changing anything ` +
  `(the briefs are not part of it: each worker reads its own from the plan). ` +
  `Return in done_tasks the list "integrated" printed by python3 .claude/scripts/tickets/ticket_tree.py status --ticket ${ID} ` +
  `(the tasks already integrated, uncommitted, by an earlier run, TKT-11). ` +
  `Return in push_status the line of PLAN.md that starts with "**Push:**" (empty if there is none), and push_approved true only if that line is exactly "${PUSH_APPROVED}" (TKT-18).`,
  { agentType: 'scribe', schema: GATE, label: `gate ${ID}` },
)
if (!gate || !gate.approved) {
  return { ticket: ID, stopped: `Plan not approved (${gate ? gate.status : 'PLAN.md unreadable'}). Approve it in docs/tickets/${ID}/PLAN.md first.` }
}
const planCheck = await agent(
  WHERE + `Run exactly python3 .claude/skills/ticket/scripts/check_plan.py ${ID} and report. passed is true only if it exits 0 and prints nothing; problems lists its output lines.`,
  { agentType: 'verifier', schema: CHECK, label: `plan check ${ID}` },
)
if (!planCheck || !planCheck.passed) {
  return { ticket: ID, stopped: 'PLAN.md fails check_plan.py', problems: planCheck ? planCheck.problems : ['check_plan.py did not report'] }
}
// TKT-16: the start rule. Every prerequisite merged on develop, no open ticket on the same areas, no field ticket
// before its campaign. --force (the person's choice) logs the problems and goes on. TKT-23: a ticket already done
// (merged, or its issue closed) or already finished (its pull request open) is refused even with --force.
const startRule = await agent(
  `Run exactly python3 .claude/scripts/tickets/tickets.py check --ticket ${ID}${FORCE ? ' --force' : ''} and report. ` +
  `passed is true only if it exits 0; problems lists every line it prints.`,
  { agentType: 'verifier', schema: CHECK, label: `start rule ${ID}` },
)
if (!startRule || !startRule.passed) {
  return { ticket: ID, stopped: 'The start rule refuses this ticket for now (TKT-16)', problems: startRule ? startRule.problems : ['tickets.py check did not report'],
    next: `Wait for what it names, or run /ticket-run ${ID} --force to start anyway.` }
}
if (startRule.problems.length) note(`Started with --force despite: ${startRule.problems.join(' / ')}`, '👤 person', '⚠️')
const tasks = gate.tasks
const alreadyDone = new Set(gate.done_tasks || [])
if (alreadyDone.size) log(`Re-run: ${alreadyDone.size} task(s) already integrated on ticket/${ID} are skipped (TKT-11): ${[...alreadyDone].join(', ')}`)
// TKT-18: the person approved the push of the code they reviewed. Every task is integrated and the review is done, so
// this run only checks the code again (the person may have changed it), then commits and pushes. An approval written
// before every task is integrated does not count: the person has not seen that code yet.
const pushOnly = Boolean(gate.push_approved && tasks.every(t => alreadyDone.has(t.id)))
if (pushOnly) {
  log(`Push approved by the person (TKT-18): checks, then the commit and the pull request`)
  note('Push approved after the code review', '👤 person', '🟢')
}
const waveCount = Math.max(...tasks.map(t => t.wave))
const prepared = await agent(
  `Ticket ${ID}: run python3 .claude/scripts/tickets/ticket_tree.py prepare --ticket ${ID} from the main checkout: it puts the main checkout on ` +
  `feature/tickets, the branch every running ticket shares (from origin/develop when no other ticket runs), and records the ticket's own files (TKT-16). ` +
  `Return its "home" in home and its "tree" in tree. Then run python3 .claude/scripts/github/board.py move --ticket ${ID} --status running; ` +
  `if board.py fails (gh missing or offline), say so in conflicts_resolved and go on. If prepare refuses, put its reason in blocked and change nothing.`,
  { agentType: 'integrator', schema: MERGE, label: `integrator prepare ${ID}` },
)
if (!prepared || prepared.blocked.length || !prepared.home) {
  return { ticket: ID, stopped: `The main checkout could not take the ticket on feature/tickets (TKT-16)`, problems: prepared ? prepared.blocked : ['prepare did not report'] }
}
HOME = prepared.home
log(`Ticket ${ID} works in ${HOME} on feature/tickets`)
if (/^[0-9a-f]{7,40}$/.test(prepared.tree)) currentTree = prepared.tree

// Waves --------------------------------------------------------------------------------------------------------
phase('Waves')
const assumptions = []
const decisions = []
function collect(results) {
  results.forEach(r => {
    if (!r.result) return
    assumptions.push(...r.result.assumptions.map(a => `${r.task.id}: ${a}`))
    decisions.push(...(r.result.decisions || []).map(d => ({ task: r.task.id, ...d })))
  })
}
for (let w = 1; w <= waveCount; w++) {
  const waveTasks = tasks.filter(t => t.wave === w && !alreadyDone.has(t.id))
  if (!waveTasks.length) { log(`Wave ${w}/${waveCount}: nothing left`); continue }
  log(`Wave ${w}/${waveCount}: ${waveTasks.length} tasks`)
  let results = await runTasks(waveTasks, 'Waves')
  const retry = results.filter(r => !r.result || r.result.status !== 'done')
  if (retry.length) {
    // TKT-19: a task blocked by another task's file (most often a wrong test of wave 1) cannot fix it itself. Its owner
    // fixes it first and the fix is integrated, so that the retry starts from the corrected file instead of failing
    // the same way. The blocked task is never named in check, so that ownersOf does not send the problem back to it.
    // Only files of tasks of earlier waves are sent: a file a later wave writes is not wrong yet, only missing.
    const reported = retry.flatMap(r => ((r.result && r.result.blocked_by) || []).map(b => ({
      file: b.file, check: 'a file that stops another task', detail: `${b.problem} (reported by the task that it blocks)`,
    })))
    const blockers = reported.filter(b => ownersOf(b).every(o => Number.isInteger(o.wave) && o.wave < w))
    if (reported.length > blockers.length) {
      log(`Wave ${w}: ${reported.length - blockers.length} reported blocker(s) not sent, because no earlier task owns them: ${reported.filter(b => !blockers.includes(b)).map(b => b.file).join(', ')}`)
    }
    if (blockers.length) {
      log(`Wave ${w}: ${blockers.length} file(s) of other tasks block ${retry.length} task(s); their owners fix them before the retry (TKT-19)`)
      note(`Wave ${w}: ${blockers.length} blocking file(s) sent to their owners: ${blockers.map(b => b.file).join(', ')}`, 'workers', '🔁')
      await fixRound(blockers, 'Waves')
    }
    log(`Wave ${w}: retrying ${retry.length} task(s) once`)
    const again = await runTasks(retry.map(r => r.task), 'Waves',
      `A first attempt did not finish: ${retry.map(r => (r.result && r.result.note) || 'no result').join(' | ')}`)
    results = results.filter(r => r.result && r.result.status === 'done').concat(again)
  }
  collect(results)
  const okCount = results.filter(r => r.result && r.result.status === 'done').length
  note(`Wave ${w}: ${okCount} of ${results.length} tasks done`, 'workers', okCount === results.length ? '✅' : '❌')
  const failed = results.filter(r => !r.result || r.result.status !== 'done')
  await integrate(results, 'Waves')
  if (failed.length) {
    await agent(inHome(`Append to the Events table of docs/tickets/${ID}/PROGRESS.md these events (Event | By | Result): ${progress.join(' ')} and "Stopped in wave ${w}: ${failed.map(f => f.task.id).join(', ')} not done" (❌). ` +
      `Then run ${TIMINGS}.`),
      { agentType: 'scribe', label: `scribe ${ID}` })
    return { ticket: ID, stopped: `Wave ${w}: ${failed.map(f => f.task.id).join(', ')} not done after one retry`, assumptions,
      next: `The integrated work stays uncommitted in ${HOME} on feature/tickets; /ticket-run ${ID} continues from wave ${w} (TKT-11).` }
  }
}

phase('Verify')
let verdict = null
for (let round = 0; round <= MAX_FIX_ROUNDS; round++) {
  verdict = await agent(inHome(`Verify ticket ${ID}: python3 .claude/scripts/tickets/checks.py --ticket ${ID} checks only its own files.`), { agentType: 'verifier', schema: VERDICT, phase: 'Verify', label: `verifier round ${round + 1}` })
  note(`Verify ${round + 1}${verdict && verdict.not_applicable && verdict.not_applicable.length ? ` (${verdict.not_applicable.length} not applicable)` : ''}`, 'verifier', verdict && verdict.passed ? '✅ passed' : `❌ ${verdict ? verdict.failures.length : '?'} failures`)
  if (!verdict || verdict.passed || round === MAX_FIX_ROUNDS) break
  // TKT-6: a missing tool or module is the environment's fault; fixers cannot repair it, so stop at once.
  if (verdict.failures.some(f => f.environment)) {
    log(`Environment failure (${verdict.failures.filter(f => f.environment).map(f => f.check).join(', ')}): no fix round, the person fixes the environment`)
    break
  }
  await fixRound(verdict.failures, 'Verify')
}
const environmentFailure = Boolean(verdict && !verdict.passed && verdict.failures.some(f => f.environment))

phase('Review')
// TKT-12: round 1 reviews the whole ticket; later rounds only confirm the fixes. Only blocking findings are fixed;
// follow-ups are recorded and never hold the merge.
let review = null
let blocking = []
const followUps = []
function keep(findings) {
  for (const f of findings.filter(x => x.severity !== 'blocking')) {
    if (!followUps.some(x => x.file === f.file && x.change === f.change)) followUps.push(f)
  }
  return findings.filter(x => x.severity === 'blocking')
}
if (pushOnly) log('Review skipped: it was done before the person reviewed the code (TKT-18)')
if (verdict && verdict.passed && !pushOnly) {
  let reviewedTree = null
  for (let round = 0; round <= MAX_FIX_ROUNDS; round++) {
    const prompt = inHome(round === 0
      ? `Review ticket ${ID} (mode: full review): its uncommitted work, python3 .claude/scripts/tickets/ticket_tree.py diff --ticket ${ID}, against docs/tickets/${ID}/TICKET.md. ` +
        `Assumptions reported by the agents: ${JSON.stringify(assumptions)}. ` +
        `Decisions reported by the agents: ${JSON.stringify(decisions)}. ` +
        `Return in note the short review note, following .claude/skills/ticket/templates/REVIEW.md.`
      : `Review ticket ${ID} (mode: confirm fixes, round ${round + 1}). Previous blocking findings: ${JSON.stringify(blocking)}. ` +
        `The fixes are in python3 .claude/scripts/tickets/ticket_tree.py diff --ticket ${ID} --from ${reviewedTree}. Report, as blocking, only (a) a previous blocking finding that is not resolved, ` +
        `and (b) a blocking defect introduced by that diff. Anything else is a follow-up. List in resolved the previous findings now fixed. ` +
        `Return in note the short review note, following .claude/skills/ticket/templates/REVIEW.md.`)
    review = await agent(prompt, { agentType: 'reviewer', schema: REVIEW, phase: 'Review', label: `reviewer round ${round + 1}` })
    if (!review) break
    blocking = keep(review.findings)
    note(`Review ${round + 1} (${round === 0 ? 'full' : 'confirm fixes'})`, 'reviewer',
      `${blocking.length ? '⚠️' : '✅'} ${blocking.length} blocking, ${review.findings.length - blocking.length} follow-ups`)
    if (!blocking.length || round === MAX_FIX_ROUNDS) break
    reviewedTree = currentTree
    await fixRound(blocking.map(f => ({ file: f.file, check: f.rule, detail: f.change })), 'Review')
    verdict = await agent(inHome(`Verify ticket ${ID}: python3 .claude/scripts/tickets/checks.py --ticket ${ID} checks only its own files.`), { agentType: 'verifier', schema: VERDICT, phase: 'Review', label: `verifier after review ${round + 1}` })
    if (!verdict || !verdict.passed) break
  }
}
if (followUps.length) log(`${followUps.length} follow-up(s) recorded, not blocking (TKT-12)`)

// Finish -------------------------------------------------------------------------------------------------------
// TKT-5: nothing is committed before this point. The documents are written first, so that the ticket's single commit
// holds them with the work. TKT-18: the run that completes the work stops here for the person to review the code; only
// a run after they approved the push (pushOnly) makes the commit and the push, the last writes of the ticket.
phase('Finish')
const done = Boolean(verdict && verdict.passed && (pushOnly || (review && blocking.length === 0)))
const followUpRows = followUps.map(f => ({ file: f.file, change: f.change }))
const scribeWork = agent(inHome(
  `Ticket ${ID}: append to the Events table of docs/tickets/${ID}/PROGRESS.md these events (Event | By | Result): ${progress.join(' ')}. ` +
  (done
    ? (pushOnly
      ? ''
      : `Set TICKET.md status to "✅ Done". In docs/tickets/${ID}/PLAN.md, put the line "${PUSH_AWAITING}" on its own paragraph right after ` +
        `the "**Plan:**" status line, replacing any line that starts with "**Push:**" (TKT-18). ` +
        `Add a row "Waiting for the person's code review: nothing is committed or pushed until PLAN.md says ${PUSH_APPROVED} (TKT-18)" (👀).`)
    : `Add a row "Stopped: ${environmentFailure ? 'environment problem (missing tool or module), the person fixes the environment and re-runs' : verdict && !verdict.passed ? 'checks failing' : 'blocking review findings left after the fix rounds; the person decides'}" (❌) with the open failures or findings: ${JSON.stringify(verdict && !verdict.passed ? verdict.failures : blocking)}. ` +
      `Add a row "Work left uncommitted in ${HOME} on feature/tickets; /ticket-run ${ID} continues it" (⚠️).`) +
  (review ? ` Write docs/tickets/${ID}/REVIEW.md exactly from the note of the last review: ${JSON.stringify(review.note)}.` : '') +
  (followUps.length ? ` Add a section "## 🔜 Follow-ups" to PROGRESS.md listing these non-blocking findings, one row each (file, what to change): ${JSON.stringify(followUpRows)}.` : '') +
  (done ? '' : ` Finally run ${TIMINGS}.`)),
  { agentType: 'scribe', phase: 'Finish', label: `scribe ${ID}` },
)
let finished = null
let awaitingReview = false
if (done) {
  if (pushOnly) {
    await scribeWork
  } else {
    // TKT-14: EXPLAIN.md and IMPLEMENTATION.md are written beside the scribe's documents (different files).
    await Promise.all([
      scribeWork,
      agent(inHome(
        `Ticket ${ID} is done; its work is uncommitted in the main checkout on feature/tickets (python3 .claude/scripts/tickets/ticket_tree.py diff --ticket ${ID} shows only its own files). Write docs/tickets/${ID}/EXPLAIN.md and ` +
        `docs/tickets/${ID}/IMPLEMENTATION.md following your instructions and the templates of .claude/skills/ticket/templates/. ` +
        `Decisions reported by the agents: ${JSON.stringify(decisions)}. ` +
        `Assumptions accepted by the reviewer: ${JSON.stringify(review.assumptions_accepted)}. ` +
        `Review note: ${JSON.stringify(review.note)}. ` +
        `Follow-ups (for EXPLAIN.md): ${JSON.stringify(followUpRows)}.`),
        { agentType: 'explainer', phase: 'Finish', label: `explainer ${ID}` },
      ),
    ])
  }
  // TKT-14: every file and line of EXPLAIN.md and IMPLEMENTATION.md is a working clickable link. ticket_tree.py docs
  // checks it deterministically; the explainer fixes what it reports once, and finish refuses to commit otherwise. After
  // the person's review it runs again, because a change they made can leave the table of changes out of date.
  for (let round = 0; round <= 1; round++) {
    const docsCheck = await agent(inHome(
      `Run exactly python3 .claude/scripts/tickets/ticket_tree.py docs --ticket ${ID} and report. passed is true only if it exits 0 and prints nothing; problems lists its output lines.`),
      { agentType: 'verifier', schema: CHECK, phase: 'Finish', label: `docs check ${ID} ${round + 1}` },
    )
    log(`Documents check ${round + 1}: ${docsCheck && docsCheck.passed ? 'passed' : `${docsCheck ? docsCheck.problems.length : '?'} problem(s)`}`)
    if (!docsCheck || docsCheck.passed || round === 1) break
    await agent(inHome(
      `Ticket ${ID}: fix only these problems of docs/tickets/${ID}/EXPLAIN.md and IMPLEMENTATION.md, so that every file and line ` +
      `they mention is a clickable link that opens it (TKT-14); when the table of changes is out of date, rewrite it with ` +
      `python3 .claude/scripts/tickets/ticket_tree.py changes --ticket ${ID} --write. Then run python3 .claude/scripts/tickets/ticket_tree.py docs --ticket ${ID} until it prints nothing: ` +
      `${JSON.stringify(docsCheck.problems)}`),
      { agentType: 'explainer', phase: 'Finish', label: `explainer ${ID} (fix links)` },
    )
  }
  if (pushOnly) {
    finished = await agent(inHome(
      `Ticket ${ID} is done and the person reviewed its code and approved the push (TKT-18). First run ${TIMINGS}, ` +
      `then python3 .claude/scripts/tickets/ticket_tree.py finish --ticket ${ID}: the ticket's single commit on feature/tickets, holding only its own files ` +
      `(the other running tickets stay uncommitted), pushed, with the pull request of feature/tickets to develop opened or updated (Closes its issue, ` +
      `label automerge); GitHub merges it once CI passes (TKT-15). ` +
      `Never push or merge yourself. Put anything that stops it in blocked, the commit in tree, and the pull request's URL in pull_request.`),
      { agentType: 'integrator', schema: MERGE, phase: 'Finish', label: `integrator finish ${ID}` },
    )
  } else {
    awaitingReview = true
    await agent(inHome(`Ticket ${ID}: run ${TIMINGS}. Commit nothing (TKT-18).`),
      { agentType: 'scribe', phase: 'Finish', label: `scribe ${ID} (timings)` })
  }
} else {
  await scribeWork
}
const merged = Boolean(finished && !finished.blocked.length)
const pullRequest = finished && finished.pull_request ? finished.pull_request : ''

return {
  ticket: ID,
  done,
  published: merged,
  home: HOME,
  pullRequest,
  tasks: tasks.length,
  waves: waveCount,
  checks: verdict ? (verdict.passed ? 'passed' : `${verdict.failures.length} failing`) : 'not run',
  review: review ? (blocking.length ? `${blocking.length} blocking left` : 'approved') : 'not run',
  followUps: followUps.length,
  reviewNote: review ? `docs/tickets/${ID}/REVIEW.md` : 'not written',
  documents: done ? [`docs/tickets/${ID}/EXPLAIN.md`, `docs/tickets/${ID}/IMPLEMENTATION.md`] : [],
  assumptions,
  decisions: decisions.length,
  awaitingReview,
  next: awaitingReview
    ? `Review the code before anything is committed or pushed (TKT-18): it is uncommitted in ${HOME} on feature/tickets ` +
      `(python3 .claude/scripts/tickets/ticket_tree.py diff --ticket ${ID} shows only this ticket's files; VS Code's Source Control shows every running ticket), explained file by file in ` +
      `${HOME}/docs/tickets/${ID}/EXPLAIN.md. When it suits you, change "${PUSH_AWAITING}" to "${PUSH_APPROVED}" in ` +
      `${HOME}/docs/tickets/${ID}/PLAN.md and run /ticket-run ${ID}: it checks the code again, then commits and pushes it with its pull request.`
    : merged ? (pullRequest
      ? `Pull request ${pullRequest}: GitHub merges it into develop once CI passes, the issue closes and the card moves to 🏁 Done. Once every running ticket is merged, python3 .claude/scripts/tickets/tickets.py prune puts the main checkout back on develop.`
      : `One commit on feature/tickets, merged into develop locally (no remote).`)
    : done ? `The documents are written but the commit or the merge stopped: ${finished ? finished.blocked.join('; ') : 'the integrator did not report'}`
    : environmentFailure ? `Fix the environment (see the failing checks in ${HOME}/docs/tickets/${ID}/PROGRESS.md), then run /ticket-run ${ID} again. The work stays uncommitted in ${HOME}.`
    : `See ${HOME}/docs/tickets/${ID}/PROGRESS.md. The work stays uncommitted in ${HOME} on feature/tickets.`,
}
