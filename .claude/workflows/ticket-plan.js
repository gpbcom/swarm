export const meta = {
  name: 'ticket-plan',
  description: 'Open a roadmap ticket and plan it as a parallel task graph, then stop for the person to approve the plan',
  whenToUse: 'Start a ticket of the Swarm roadmap, for example /ticket-plan T1.07 (TKT rules in .claude/rules/tickets.md)',
  phases: [
    { title: 'Ticket', detail: 'ticket-writer writes TICKET.md and PROGRESS.md' },
    { title: 'Check', detail: 'check_ticket.py checks the IDs, links and sections of TICKET.md' },
    { title: 'Plan', detail: 'planner designs the task graph; waves and file ownership computed in code' },
    { title: 'Write', detail: 'scribe writes PLAN.md, awaiting approval' },
  ],
}

const ID = String(typeof args === 'string' ? args : (args && args.ticket) || '').trim()
if (!/^T\d\.\d{2}$/.test(ID)) throw new Error('Usage: /ticket-plan T1.07 (a ticket ID of the roadmap)')

const WORKERS = ['test-writer', 'implementer', 'rust-implementer', 'frontend-implementer', 'mockup-writer', 'doc-writer']

const TICKET_SCHEMA = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    title: { type: 'string' },
    criteria: { type: 'integer' },
    specs: { type: 'array', items: { type: 'string' } },
    assumptions: { type: 'array', items: { type: 'string' } },
  },
  required: ['id', 'title', 'criteria', 'specs', 'assumptions'],
}

const CHECK = {
  type: 'object',
  properties: { passed: { type: 'boolean' }, problems: { type: 'array', items: { type: 'string' } } },
  required: ['passed', 'problems'],
}

const WRITE_SCHEMA = {
  type: 'object',
  properties: {
    written: { type: 'array', items: { type: 'string' } },
    problems: { type: 'array', items: { type: 'string' } },
  },
  required: ['written', 'problems'],
}

const PLAN_SCHEMA = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    tasks: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          title: { type: 'string' },
          agent: { type: 'string', enum: WORKERS },
          depends_on: { type: 'array', items: { type: 'string' } },
          files: { type: 'array', items: { type: 'string' } },
          brief: { type: 'string' },
          done_when: { type: 'string' },
        },
        required: ['id', 'title', 'agent', 'depends_on', 'files', 'brief', 'done_when'],
      },
    },
    assumptions: { type: 'array', items: { type: 'string' } },
  },
  required: ['summary', 'tasks', 'assumptions'],
}

// Waves: a task runs after all its dependencies; two tasks of one wave never share a file (TKT-4).
function computeWaves(tasks) {
  const byId = Object.fromEntries(tasks.map(t => [t.id, t]))
  for (const t of tasks) {
    const known = t.depends_on.filter(d => byId[d] && d !== t.id)
    if (known.length !== t.depends_on.length) log(`${t.id}: unknown dependencies dropped`)
    t.depends_on = known
  }
  const wave = {}
  const visiting = new Set()
  function level(t) {
    if (wave[t.id] !== undefined) return wave[t.id]
    if (visiting.has(t.id)) throw new Error(`Dependency cycle through ${t.id}`)
    visiting.add(t.id)
    wave[t.id] = 1 + Math.max(0, ...t.depends_on.map(d => level(byId[d])))
    visiting.delete(t.id)
    return wave[t.id]
  }
  tasks.forEach(level)
  let changed = true
  while (changed) {
    changed = false
    const owners = {}
    for (const t of [...tasks].sort((a, b) => wave[a.id] - wave[b.id] || a.id.localeCompare(b.id))) {
      for (const d of t.depends_on) {
        if (wave[t.id] <= wave[d]) { wave[t.id] = wave[d] + 1; changed = true }
      }
      const clash = t.files.find(f => owners[`${wave[t.id]}|${f}`] && owners[`${wave[t.id]}|${f}`] !== t.id)
      if (clash) {
        log(`${t.id} shares ${clash} with ${owners[`${wave[t.id]}|${clash}`]}: moved to wave ${wave[t.id] + 1}`)
        wave[t.id] += 1
        changed = true
        break
      }
      t.files.forEach(f => { owners[`${wave[t.id]}|${f}`] = t.id })
    }
  }
  return tasks.map(t => ({ ...t, wave: wave[t.id] })).sort((a, b) => a.wave - b.wave || a.id.localeCompare(b.id))
}

phase('Ticket')
const ticket = await agent(
  `Open ticket ${ID} of the Swarm roadmap: write docs/tickets/${ID}/TICKET.md and PROGRESS.md, keeping them if they already exist and are complete. ` +
  `TICKET.md must link at least one technical page, feature, use case or business rule (TKT-2); return those links in specs.`,
  { agentType: 'ticket-writer', schema: TICKET_SCHEMA, label: `ticket-writer ${ID}` },
)
if (!ticket) throw new Error(`ticket-writer failed for ${ID}`)
if (!ticket.specs.length) {
  return {
    ticket: ID,
    stopped: 'TICKET.md links no technical page, feature, use case or business rule (TKT-2). Write or point to the specification the ticket builds on, then run /ticket-plan again.',
    assumptions: ticket.assumptions,
  }
}
log(`TICKET.md refers to ${ticket.specs.length} specification page(s)`)

phase('Check')
const checkTicket = () => agent(
  `From the repository root, run exactly: python3 .claude/skills/ticket/scripts/check_ticket.py ${ID}. ` +
  `Return passed (true when it exits 0 and prints nothing) and, in problems, every line it printed.`,
  { agentType: 'verifier', schema: CHECK, label: `check TICKET.md ${ID}` },
)
let ticketCheck = await checkTicket()
if (!ticketCheck || !ticketCheck.passed) {
  const first = (ticketCheck && ticketCheck.problems) || ['the verifier returned no result']
  log(`TICKET.md fails check_ticket.py: ${first.join(' | ')}`)
  await agent(
    `Fix only docs/tickets/${ID}/TICKET.md so that python3 .claude/skills/ticket/scripts/check_ticket.py ${ID} passes. ` +
    `Its problems: ${JSON.stringify(first)}. Change nothing else.`,
    { agentType: 'ticket-writer', schema: TICKET_SCHEMA, label: `ticket-writer fix ${ID}` },
  )
  ticketCheck = await checkTicket()
  if (!ticketCheck || !ticketCheck.passed) {
    return {
      ticket: ID,
      stopped: 'TICKET.md fails check_ticket.py',
      problems: (ticketCheck && ticketCheck.problems) || ['the verifier returned no result'],
    }
  }
}

phase('Plan')
const plan = await agent(
  `Plan ticket ${ID} from docs/tickets/${ID}/TICKET.md as a task graph for parallel worker agents. ` +
  `Every brief links the specification pages of TICKET.md that its task applies (TKT-2).`,
  { agentType: 'planner', schema: PLAN_SCHEMA, label: `planner ${ID}` },
)
if (!plan || !plan.tasks.length) throw new Error(`planner returned no task for ${ID}`)
const graph = computeWaves(plan.tasks)
const waves = Math.max(...graph.map(t => t.wave))
const widest = Math.max(...Array.from({ length: waves }, (_, i) => graph.filter(t => t.wave === i + 1).length))
log(`${graph.length} tasks in ${waves} waves, widest wave ${widest} (at most 8 agents run at once)`)

phase('Write')
const written = await agent(
  `Write docs/tickets/${ID}/PLAN.md for ticket ${ID} (${ticket.title}) with the status line "**Plan:** 🟡 Awaiting approval", ` +
  `this summary: ${JSON.stringify(plan.summary)}, the assumptions ${JSON.stringify([...ticket.assumptions, ...plan.assumptions])}, ` +
  `then a "## Task graph" heading and this task graph in a json block, exactly: ${JSON.stringify(graph)}. ` +
  `Then run python3 .claude/scripts/plan.py render --ticket ${ID}, which pretty-prints the json block and writes from it the waves table, ` +
  `the dependency graph and one section per task for the person; it must print nothing. Then append to the Events table of docs/tickets/${ID}/PROGRESS.md: "Plan written: ${graph.length} tasks, ${waves} waves" (⏳ Awaiting approval), ` +
  `Then run python3 .claude/scripts/ticket_refs.py sync --ticket ${ID}, which copies the specification references of TICKET.md into PLAN.md and PROGRESS.md, ` +
  `and python3 .claude/scripts/progress.py timings --ticket ${ID} --write. ` +
  `Then run python3 .claude/scripts/board.py move --ticket ${ID} --status planned, which moves its card to 📝 Planned on the GitHub board (TKT-17); ` +
  `if it fails because gh is missing or offline, go on. ` +
  `Last, run python3 .claude/scripts/ticket_refs.py check --ticket ${ID} and python3 .claude/scripts/plan.py check --ticket ${ID}, ` +
  `and return in problems every line they print (none when all is well).`,
  { agentType: 'scribe', schema: WRITE_SCHEMA, label: `scribe ${ID}` },
)
const problems = (written && written.problems) || ['the scribe returned no result']
if (problems.length) log(`PLAN.md, PROGRESS.md or TICKET.md fails its checks: ${problems.join(' | ')}`)

const planVerdict = await agent(
  `From the repository root, run exactly: python3 .claude/skills/ticket/scripts/check_plan.py ${ID}. ` +
  `Return passed (true when it exits 0 and prints nothing) and, in problems, every line it printed.`,
  { agentType: 'verifier', schema: CHECK, label: `check PLAN.md ${ID}` },
)
let planCheck = 'passed'
if (!planVerdict || !planVerdict.passed) {
  const planProblems = (planVerdict && planVerdict.problems) || ['the verifier returned no result']
  planCheck = planProblems
  log(`PLAN.md fails check_plan.py: ${planProblems.join(' | ')}`)
  await agent(
    `Append to the Events table of docs/tickets/${ID}/PROGRESS.md the row "Plan check failed: ${planProblems.length} problems" (⚠️). Change nothing else.`,
    { agentType: 'scribe', schema: WRITE_SCHEMA, label: `scribe plan check ${ID}` },
  )
}

return {
  ticket: ID,
  title: ticket.title,
  tasks: graph.length,
  waves,
  widestWave: widest,
  specs: ticket.specs,
  planCheck,
  checks: problems.length ? problems : 'passed',
  assumptions: [...ticket.assumptions, ...plan.assumptions],
  next: `Review docs/tickets/${ID}/PLAN.md, change its status to "**Plan:** 🟢 Approved", then run /ticket-run ${ID}: it gives the ticket its own worktree on feature/${ID}, so other tickets can run at the same time (TKT-16)`,
}
