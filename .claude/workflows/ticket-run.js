export const meta = {
  name: 'ticket-run',
  description: 'Run an approved ticket plan: parallel worktree waves handed off uncommitted, integration, verification, review, EXPLAIN.md and IMPLEMENTATION.md, then one commit merged into develop locally (never pushed)',
  whenToUse: 'After the person approved docs/tickets/<ID>/PLAN.md, for example /ticket-run T1.07 (TKT rules in .claude/rules/tickets.md)',
  phases: [
    { title: 'Gate', detail: 'refuse unless PLAN.md is approved' },
    { title: 'Waves', detail: 'workers in their own worktrees, at most 8 at once, hand off uncommitted; integrator applies each wave' },
    { title: 'Verify', detail: 'verifier runs every check; owners fix failures, at most twice' },
    { title: 'Review', detail: 'reviewer gates the diff; owners fix findings, at most twice' },
    { title: 'Finish', detail: 'EXPLAIN.md, IMPLEMENTATION.md, REVIEW.md, PROGRESS.md, then the single commit merged into develop' },
  ],
}

const ID = String(typeof args === 'string' ? args : (args && args.ticket) || '').trim()
if (!/^T\d\.\d{2}$/.test(ID)) throw new Error('Usage: /ticket-run T1.07 (a ticket ID of the roadmap)')
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
  },
  required: ['approved', 'status', 'tasks', 'done_tasks'],
}
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
// The tree of the integrated, uncommitted work after the last integration (TKT-5): the confirm-fixes review diffs from it.
let currentTree = ''
function note(event, by, result) { progress.push(`| ${event} | ${by} | ${result} |`) }

function workerPrompt(t, extra) {
  return `Ticket ${ID}, task ${t.id}: ${t.title}.\nYour worktree branches from ticket/${ID}, whose work is uncommitted (TKT-5). ` +
    `First run python3 .claude/scripts/ticket_tree.py start --ticket ${ID} at the root of your worktree: it copies that work in.\n` +
    `Files you may change: ${t.files.join(', ')}.\n` +
    (!/^K\d{2}$/.test(t.id)
      ? `Brief: ${t.brief}\nDone when: ${t.done_when}\n`
      : `First read your brief and done-when exactly as approved: run python3 .claude/scripts/plan.py task --ticket ${ID} --id ${t.id} ` +
        `at the root of your worktree. Follow them as your brief.\n`) +
    (extra ? `\n${extra}\n` : '') +
    `Never commit, push or merge. Last, run python3 .claude/scripts/ticket_tree.py handoff --ticket ${ID} --task ${t.id} ` +
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
  const merge = await agent(
    `Ticket ${ID}: integrate the hand-offs of these tasks into the main checkout, in this order: ` +
    `python3 .claude/scripts/ticket_tree.py integrate --ticket ${ID} ${ids.map(id => `--task ${JSON.stringify(id)}`).join(' ')}. ` +
    `Then run the quick checks for what they changed (ruff check, cargo check or tsc as relevant). Commit nothing (TKT-5).`,
    { agentType: 'integrator', schema: MERGE, phase: label, label: `integrator ${label}` },
  )
  note(`Integrate (${label})`, 'integrator', merge ? `✅ ${merge.integrated.length} integrated, ${merge.blocked.length} blocked, not committed` : '❌ failed')
  if (merge && /^[0-9a-f]{7,40}$/.test(merge.tree)) currentTree = merge.tree
  return merge
}

// Gate ---------------------------------------------------------------------------------------------------------
phase('Gate')
const gate = await agent(
  `Read docs/tickets/${ID}/PLAN.md. approved is true only if its status line is exactly "**Plan:** 🟢 Approved". ` +
  `Return the status line, and in tasks the JSON array printed by python3 .claude/scripts/plan.py outline --ticket ${ID}, exactly, without changing anything ` +
  `(the briefs are not part of it: each worker reads its own from the plan). ` +
  `Return in done_tasks the list "integrated" printed by python3 .claude/scripts/ticket_tree.py status --ticket ${ID} ` +
  `(the tasks already integrated, uncommitted, by an earlier run, TKT-11).`,
  { agentType: 'scribe', schema: GATE, label: `gate ${ID}` },
)
if (!gate || !gate.approved) {
  return { ticket: ID, stopped: `Plan not approved (${gate ? gate.status : 'PLAN.md unreadable'}). Approve it in docs/tickets/${ID}/PLAN.md first.` }
}
const planCheck = await agent(
  `Run exactly python3 .claude/skills/ticket/scripts/check_plan.py ${ID} and report. passed is true only if it exits 0 and prints nothing; problems lists its output lines.`,
  { agentType: 'verifier', schema: CHECK, label: `plan check ${ID}` },
)
if (!planCheck || !planCheck.passed) {
  return { ticket: ID, stopped: 'PLAN.md fails check_plan.py', problems: planCheck ? planCheck.problems : ['check_plan.py did not report'] }
}
const tasks = gate.tasks
const alreadyDone = new Set(gate.done_tasks || [])
if (alreadyDone.size) log(`Re-run: ${alreadyDone.size} task(s) already integrated on ticket/${ID} are skipped (TKT-11): ${[...alreadyDone].join(', ')}`)
const waveCount = Math.max(...tasks.map(t => t.wave))
const prepared = await agent(
  `Ticket ${ID}: run python3 .claude/scripts/ticket_tree.py prepare --ticket ${ID} in the main checkout. ` +
  `If it refuses, put each file it names in blocked and change nothing.`,
  { agentType: 'integrator', schema: MERGE, label: `integrator prepare ${ID}` },
)
if (!prepared || prepared.blocked.length) {
  return { ticket: ID, stopped: `The main checkout cannot hold the ticket's uncommitted work (TKT-5)`, problems: prepared ? prepared.blocked : ['prepare did not report'] }
}
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
    await agent(`Append to the Events table of docs/tickets/${ID}/PROGRESS.md these events (Event | By | Result): ${progress.join(' ')} and "Stopped in wave ${w}: ${failed.map(f => f.task.id).join(', ')} not done" (❌). ` +
      `Then run python3 .claude/scripts/progress.py timings --ticket ${ID} --write.`,
      { agentType: 'scribe', label: `scribe ${ID}` })
    return { ticket: ID, stopped: `Wave ${w}: ${failed.map(f => f.task.id).join(', ')} not done after one retry`, assumptions,
      next: `The integrated work stays uncommitted on ticket/${ID}; /ticket-run ${ID} continues from wave ${w} (TKT-11).` }
  }
}

// Fix loop: send each failure or finding to the task that owns it, each fixer only its own problems --------------
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
function ownerOf(item) {
  const hinted = String(item.detail || '').match(/\bK\d{2}\b/g) || []
  const byHint = hinted.map(id => tasks.find(t => t.id === id)).find(Boolean)
  if (byHint) return byHint
  const files = String(item.file || '').split(',').map(normalise).filter(Boolean)
  for (const f of files) {
    const dir = f.replace(/\/$/, '') + '/'
    const owner = tasks.find(t => t.files.some(x => x === f || x.endsWith('/' + f) || f.endsWith('/' + x) || x.startsWith(dir)))
    if (owner) return owner
  }
  const f = files[0] || 'unknown'
  return { id: `FIX-${f}`, title: `Fix ${f}`, agent: agentFor(f), files, brief: '', done_when: 'the verifier passes' }
}
async function fixRound(items, label) {
  const groups = {}
  for (const it of items) {
    const owner = ownerOf(it)
    groups[owner.id] = groups[owner.id] || { task: owner, items: [] }
    groups[owner.id].items.push(it)
  }
  log(`${label}: ${items.length} problem(s) sent to ${Object.keys(groups).length} fixer(s): ${Object.keys(groups).join(', ')}`)
  const results = await limited(Object.values(groups), MAX_PARALLEL, g =>
    agent(workerPrompt(g.task, `Fix only these problems, within your files: ${JSON.stringify(g.items)}`), {
      agentType: g.task.agent, isolation: 'worktree', schema: RESULT, phase: label, label: `${g.task.id} ${g.task.agent} (fix)`,
    }).then(r => ({ task: g.task, result: r })))
  collect(results)
  await integrate(results, label)
}

phase('Verify')
let verdict = null
for (let round = 0; round <= MAX_FIX_ROUNDS; round++) {
  verdict = await agent(`Verify ticket ${ID} on ticket/${ID}.`, { agentType: 'verifier', schema: VERDICT, phase: 'Verify', label: `verifier round ${round + 1}` })
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
if (verdict && verdict.passed) {
  let reviewedTree = null
  for (let round = 0; round <= MAX_FIX_ROUNDS; round++) {
    const prompt = round === 0
      ? `Review ticket ${ID} (mode: full review): its uncommitted work, python3 .claude/scripts/ticket_tree.py diff --ticket ${ID}, against docs/tickets/${ID}/TICKET.md. ` +
        `Assumptions reported by the agents: ${JSON.stringify(assumptions)}. ` +
        `Decisions reported by the agents: ${JSON.stringify(decisions)}. ` +
        `Return in note the short review note, following .claude/skills/ticket/templates/REVIEW.md.`
      : `Review ticket ${ID} (mode: confirm fixes, round ${round + 1}). Previous blocking findings: ${JSON.stringify(blocking)}. ` +
        `The fixes are in python3 .claude/scripts/ticket_tree.py diff --ticket ${ID} --from ${reviewedTree}. Report, as blocking, only (a) a previous blocking finding that is not resolved, ` +
        `and (b) a blocking defect introduced by that diff. Anything else is a follow-up. List in resolved the previous findings now fixed. ` +
        `Return in note the short review note, following .claude/skills/ticket/templates/REVIEW.md.`
    review = await agent(prompt, { agentType: 'reviewer', schema: REVIEW, phase: 'Review', label: `reviewer round ${round + 1}` })
    if (!review) break
    blocking = keep(review.findings)
    note(`Review ${round + 1} (${round === 0 ? 'full' : 'confirm fixes'})`, 'reviewer',
      `${blocking.length ? '⚠️' : '✅'} ${blocking.length} blocking, ${review.findings.length - blocking.length} follow-ups`)
    if (!blocking.length || round === MAX_FIX_ROUNDS) break
    reviewedTree = currentTree
    await fixRound(blocking.map(f => ({ file: f.file, check: f.rule, detail: f.change })), 'Review')
    verdict = await agent(`Verify ticket ${ID} on ticket/${ID}.`, { agentType: 'verifier', schema: VERDICT, phase: 'Review', label: `verifier after review ${round + 1}` })
    if (!verdict || !verdict.passed) break
  }
}
if (followUps.length) log(`${followUps.length} follow-up(s) recorded, not blocking (TKT-12)`)

// Finish -------------------------------------------------------------------------------------------------------
// TKT-5: nothing is committed before this point. The documents are written first, so that the ticket's single commit
// holds them with the work; the commit and the merge into develop are the last writes of the run.
phase('Finish')
const done = Boolean(verdict && verdict.passed && review && blocking.length === 0)
const followUpRows = followUps.map(f => ({ file: f.file, change: f.change }))
const scribeWork = agent(
  `Ticket ${ID}: append to the Events table of docs/tickets/${ID}/PROGRESS.md these events (Event | By | Result): ${progress.join(' ')}. ` +
  (done
    ? `Set TICKET.md status to "✅ Done".`
    : `Add a row "Stopped: ${environmentFailure ? 'environment problem (missing tool or module), the person fixes the environment and re-runs' : verdict && !verdict.passed ? 'checks failing' : 'blocking review findings left after the fix rounds; the person decides'}" (❌) with the open failures or findings: ${JSON.stringify(verdict && !verdict.passed ? verdict.failures : blocking)}. ` +
      `Add a row "Work left uncommitted on ticket/${ID}; /ticket-run ${ID} continues it" (⚠️).`) +
  (review ? ` Write docs/tickets/${ID}/REVIEW.md exactly from the note of the last review: ${JSON.stringify(review.note)}.` : '') +
  (followUps.length ? ` Add a section "## 🔜 Follow-ups" to PROGRESS.md listing these non-blocking findings, one row each (file, what to change): ${JSON.stringify(followUpRows)}.` : '') +
  (done ? '' : ` Finally run python3 .claude/scripts/progress.py timings --ticket ${ID} --write.`),
  { agentType: 'scribe', phase: 'Finish', label: `scribe ${ID}` },
)
let finished = null
if (done) {
  // TKT-14: EXPLAIN.md and IMPLEMENTATION.md are written beside the scribe's documents (different files).
  await Promise.all([
    scribeWork,
    agent(
      `Ticket ${ID} is done; its work is uncommitted in the main checkout on ticket/${ID}. Write docs/tickets/${ID}/EXPLAIN.md and ` +
      `docs/tickets/${ID}/IMPLEMENTATION.md following your instructions and the templates of .claude/skills/ticket/templates/. ` +
      `Decisions reported by the agents: ${JSON.stringify(decisions)}. ` +
      `Assumptions accepted by the reviewer: ${JSON.stringify(review.assumptions_accepted)}. ` +
      `Review note: ${JSON.stringify(review.note)}. ` +
      `Follow-ups (for EXPLAIN.md): ${JSON.stringify(followUpRows)}.`,
      { agentType: 'explainer', phase: 'Finish', label: `explainer ${ID}` },
    ),
  ])
  finished = await agent(
    `Ticket ${ID} is done. First run python3 .claude/scripts/progress.py timings --ticket ${ID} --write, ` +
    `then python3 .claude/scripts/ticket_tree.py finish --ticket ${ID}: the ticket's single commit, merged into develop with --no-ff. ` +
    `Never push. Put anything that stops it in blocked, and the merge commit in tree.`,
    { agentType: 'integrator', schema: MERGE, phase: 'Finish', label: `integrator finish ${ID}` },
  )
} else {
  await scribeWork
}
const merged = Boolean(finished && !finished.blocked.length)

return {
  ticket: ID,
  done,
  merged,
  tasks: tasks.length,
  waves: waveCount,
  checks: verdict ? (verdict.passed ? 'passed' : `${verdict.failures.length} failing`) : 'not run',
  review: review ? (blocking.length ? `${blocking.length} blocking left` : 'approved') : 'not run',
  followUps: followUps.length,
  reviewNote: review ? `docs/tickets/${ID}/REVIEW.md` : 'not written',
  documents: done ? [`docs/tickets/${ID}/EXPLAIN.md`, `docs/tickets/${ID}/IMPLEMENTATION.md`] : [],
  assumptions,
  decisions: decisions.length,
  next: merged ? `One commit on ticket/${ID}, merged into develop locally. Push yourself when you want: the harness never pushes.`
    : done ? `The documents are written but the commit or the merge stopped: ${finished ? finished.blocked.join('; ') : 'the integrator did not report'}`
    : environmentFailure ? `Fix the environment (see the failing checks in docs/tickets/${ID}/PROGRESS.md), then run /ticket-run ${ID} again. The work stays uncommitted on ticket/${ID}.`
    : `See docs/tickets/${ID}/PROGRESS.md. The work stays uncommitted on ticket/${ID}.`,
}
