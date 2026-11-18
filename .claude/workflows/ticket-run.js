export const meta = {
  name: 'ticket-run',
  description: 'Run an approved ticket plan: parallel worktree waves, integration, verification, review, then a local merge into develop (never pushed)',
  whenToUse: 'After the person approved docs/tickets/<ID>/PLAN.md, for example /ticket-run T1.07 (TKT rules in .claude/rules/tickets.md)',
  phases: [
    { title: 'Gate', detail: 'refuse unless PLAN.md is approved' },
    { title: 'Waves', detail: 'workers in their own worktrees, at most 8 at once; integrator merges after each wave' },
    { title: 'Verify', detail: 'verifier runs every check; owners fix failures, at most twice' },
    { title: 'Review', detail: 'reviewer gates the diff; owners fix findings, at most twice' },
    { title: 'Finish', detail: 'merge into develop locally, EXPLAIN.md and PROGRESS.md' },
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
    brief: { type: 'string' }, done_when: { type: 'string' }, wave: { type: 'integer' },
  },
  required: ['id', 'title', 'agent', 'depends_on', 'files', 'brief', 'done_when', 'wave'],
}
const GATE = {
  type: 'object',
  properties: {
    approved: { type: 'boolean' }, status: { type: 'string' }, tasks: { type: 'array', items: TASK },
    done_tasks: { type: 'array', items: { type: 'string' } },
  },
  required: ['approved', 'status', 'tasks', 'done_tasks'],
}
const RESULT = {
  type: 'object',
  properties: {
    status: { type: 'string', enum: ['done', 'blocked', 'failed'] },
    branch: { type: 'string' }, commit: { type: 'string' },
    files_changed: { type: 'array', items: { type: 'string' } },
    checks: { type: 'array', items: { type: 'string' } },
    assumptions: { type: 'array', items: { type: 'string' } },
    note: { type: 'string' },
  },
  required: ['status', 'branch', 'files_changed', 'checks', 'assumptions'],
}
const MERGE = {
  type: 'object',
  properties: {
    merged: { type: 'array', items: { type: 'string' } },
    conflicts_resolved: { type: 'array', items: { type: 'string' } },
    blocked: { type: 'array', items: { type: 'string' } },
    head: { type: 'string' },
  },
  required: ['merged', 'blocked', 'head'],
}
const VERDICT = {
  type: 'object',
  properties: {
    passed: { type: 'boolean' },
    failures: {
      type: 'array',
      items: {
        type: 'object',
        properties: { check: { type: 'string' }, file: { type: 'string' }, detail: { type: 'string' } },
        required: ['check', 'file', 'detail'],
      },
    },
    not_applicable: { type: 'array', items: { type: 'string' } },
  },
  required: ['passed', 'failures'],
}
const REVIEW = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['approve', 'changes'] },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: { file: { type: 'string' }, rule: { type: 'string' }, change: { type: 'string' } },
        required: ['file', 'rule', 'change'],
      },
    },
    assumptions_accepted: { type: 'array', items: { type: 'string' } },
  },
  required: ['verdict', 'findings', 'assumptions_accepted'],
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
function note(event, by, result) { progress.push(`| ${event} | ${by} | ${result} |`) }

function workerPrompt(t, extra) {
  return `Ticket ${ID}, task ${t.id}: ${t.title}.\nYour worktree branches from ticket/${ID} as it is now.\n` +
    `Files you may change: ${t.files.join(', ')}.\nBrief: ${t.brief}\nDone when: ${t.done_when}\n` +
    (extra ? `\n${extra}\n` : '') +
    `Commit with the message "${ID} ${t.id}: <summary>". Never push, never merge.`
}

async function runTasks(tasks, phaseName, extra) {
  return limited(tasks, MAX_PARALLEL, t =>
    agent(workerPrompt(t, extra), {
      agentType: t.agent, isolation: 'worktree', schema: RESULT, phase: phaseName, label: `${t.id} ${t.agent}`,
    }).then(r => ({ task: t, result: r })))
}

async function integrate(results, label) {
  const branches = results.filter(r => r.result && r.result.status === 'done').map(r => r.result.branch)
  if (!branches.length) return null
  const merge = await agent(
    `Ticket ${ID}: merge these branches into ticket/${ID} in this order: ${branches.join(', ')}. ` +
    `Then run the quick checks for what they changed (ruff check, cargo check or tsc as relevant) and leave the main checkout on ticket/${ID}.`,
    { agentType: 'integrator', schema: MERGE, phase: label, label: `integrator ${label}` },
  )
  note(`Merge (${label})`, 'integrator', merge ? `✅ ${merge.merged.length} merged, ${merge.blocked.length} blocked` : '❌ failed')
  return merge
}

// Gate ---------------------------------------------------------------------------------------------------------
phase('Gate')
const gate = await agent(
  `Read docs/tickets/${ID}/PLAN.md. approved is true only if its status line is exactly "**Plan:** 🟢 Approved". ` +
  `Return the status line and the task graph of its json block exactly, without changing anything. ` +
  `If the branch ticket/${ID} exists, return in done_tasks the task ids that already have a commit on it whose message starts with "${ID} <task id>:" ` +
  `(git log ticket/${ID} --format=%s); otherwise an empty list.`,
  { agentType: 'scribe', schema: GATE, label: `gate ${ID}` },
)
if (!gate || !gate.approved) {
  return { ticket: ID, stopped: `Plan not approved (${gate ? gate.status : 'PLAN.md unreadable'}). Approve it in docs/tickets/${ID}/PLAN.md first.` }
}
const tasks = gate.tasks
const alreadyDone = new Set(gate.done_tasks || [])
if (alreadyDone.size) log(`Re-run: ${alreadyDone.size} task(s) already on ticket/${ID} are skipped (TKT-11): ${[...alreadyDone].join(', ')}`)
const waveCount = Math.max(...tasks.map(t => t.wave))
await agent(
  `Ticket ${ID}: prepare the branch ticket/${ID} from develop (create develop from the current branch if it does not exist) and leave the main checkout on it.`,
  { agentType: 'integrator', schema: MERGE, label: `integrator prepare ${ID}` },
)

// Waves --------------------------------------------------------------------------------------------------------
phase('Waves')
const assumptions = []
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
  results.forEach(r => {
    if (r.result) assumptions.push(...r.result.assumptions.map(a => `${r.task.id}: ${a}`))
  })
  const okCount = results.filter(r => r.result && r.result.status === 'done').length
  note(`Wave ${w}: ${okCount} of ${results.length} tasks done`, 'workers', okCount === results.length ? '✅' : '❌')
  const failed = results.filter(r => !r.result || r.result.status !== 'done')
  await integrate(results, 'Waves')
  if (failed.length) {
    await agent(`Append to the Events table of docs/tickets/${ID}/PROGRESS.md these events (Event | By | Result): ${progress.join(' ')} and "Stopped in wave ${w}: ${failed.map(f => f.task.id).join(', ')} not done" (❌). ` +
      `Then run python3 .claude/scripts/progress.py timings --ticket ${ID} --write.`,
      { agentType: 'scribe', label: `scribe ${ID}` })
    return { ticket: ID, stopped: `Wave ${w}: ${failed.map(f => f.task.id).join(', ')} not done after one retry`, assumptions }
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
  await integrate(results, label)
}

phase('Verify')
let verdict = null
for (let round = 0; round <= MAX_FIX_ROUNDS; round++) {
  verdict = await agent(`Verify ticket ${ID} on ticket/${ID}.`, { agentType: 'verifier', schema: VERDICT, phase: 'Verify', label: `verifier round ${round + 1}` })
  note(`Verify ${round + 1}${verdict && verdict.not_applicable && verdict.not_applicable.length ? ` (${verdict.not_applicable.length} not applicable)` : ''}`, 'verifier', verdict && verdict.passed ? '✅ passed' : `❌ ${verdict ? verdict.failures.length : '?'} failures`)
  if (!verdict || verdict.passed || round === MAX_FIX_ROUNDS) break
  await fixRound(verdict.failures, 'Verify')
}

phase('Review')
let review = null
if (verdict && verdict.passed) {
  for (let round = 0; round <= MAX_FIX_ROUNDS; round++) {
    review = await agent(
      `Review ticket ${ID}: the diff develop...ticket/${ID} against docs/tickets/${ID}/TICKET.md. Assumptions reported by the agents: ${JSON.stringify(assumptions)}`,
      { agentType: 'reviewer', schema: REVIEW, phase: 'Review', label: `reviewer round ${round + 1}` },
    )
    note(`Review ${round + 1}`, 'reviewer', review ? `${review.verdict === 'approve' ? '✅' : '⚠️'} ${review.verdict}, ${review.findings.length} findings` : '❌ no verdict')
    if (!review || review.verdict === 'approve' || round === MAX_FIX_ROUNDS) break
    await fixRound(review.findings.map(f => ({ file: f.file, check: f.rule, detail: f.change })), 'Review')
    verdict = await agent(`Verify ticket ${ID} on ticket/${ID}.`, { agentType: 'verifier', schema: VERDICT, phase: 'Review', label: `verifier after review ${round + 1}` })
    if (!verdict || !verdict.passed) break
  }
}

// Finish -------------------------------------------------------------------------------------------------------
phase('Finish')
const done = Boolean(verdict && verdict.passed && review && review.verdict === 'approve')
if (done) {
  await agent(`Ticket ${ID}: merge ticket/${ID} into develop with --no-ff, remove the merged worktrees, never push.`,
    { agentType: 'integrator', schema: MERGE, label: `integrator finish ${ID}` })
  note('Merge into develop', 'integrator', '✅ merged locally, not pushed')
}
await agent(
  `Ticket ${ID}: append to the Events table of docs/tickets/${ID}/PROGRESS.md these events (Event | By | Result): ${progress.join(' ')}. ` +
  `Finally run python3 .claude/scripts/progress.py timings --ticket ${ID} --write. ` +
  (done
    ? `Write docs/tickets/${ID}/EXPLAIN.md from TICKET.md, the diff develop~1...develop and these accepted assumptions: ${JSON.stringify(review.assumptions_accepted)}; set TICKET.md status to "✅ Done".`
    : `Add a row "Stopped: ${verdict && !verdict.passed ? 'checks failing' : 'review not approved'}" (❌) with the open failures or findings: ${JSON.stringify(verdict && !verdict.passed ? verdict.failures : (review ? review.findings : []))}.`),
  { agentType: 'scribe', label: `scribe ${ID}` },
)

return {
  ticket: ID,
  done,
  tasks: tasks.length,
  waves: waveCount,
  checks: verdict ? (verdict.passed ? 'passed' : `${verdict.failures.length} failing`) : 'not run',
  review: review ? review.verdict : 'not run',
  assumptions,
  next: done ? `Merged into develop locally. Push yourself when you want: the harness never pushes.` : `See docs/tickets/${ID}/PROGRESS.md`,
}
