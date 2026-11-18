export const meta = {
  name: 'ticket-plan',
  description: 'Open a roadmap ticket and plan it as a parallel task graph, then stop for the person to approve the plan',
  whenToUse: 'Start a ticket of the Swarm roadmap, for example /ticket-plan T1.07 (TKT rules in .claude/rules/tickets.md)',
  phases: [
    { title: 'Ticket', detail: 'ticket-writer writes TICKET.md and PROGRESS.md' },
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
    assumptions: { type: 'array', items: { type: 'string' } },
  },
  required: ['id', 'title', 'criteria', 'assumptions'],
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
  `Open ticket ${ID} of the Swarm roadmap: write docs/tickets/${ID}/TICKET.md and PROGRESS.md, keeping them if they already exist and are complete.`,
  { agentType: 'ticket-writer', schema: TICKET_SCHEMA, label: `ticket-writer ${ID}` },
)
if (!ticket) throw new Error(`ticket-writer failed for ${ID}`)

phase('Plan')
const plan = await agent(
  `Plan ticket ${ID} from docs/tickets/${ID}/TICKET.md as a task graph for parallel worker agents.`,
  { agentType: 'planner', schema: PLAN_SCHEMA, label: `planner ${ID}` },
)
if (!plan || !plan.tasks.length) throw new Error(`planner returned no task for ${ID}`)
const graph = computeWaves(plan.tasks)
const waves = Math.max(...graph.map(t => t.wave))
const widest = Math.max(...Array.from({ length: waves }, (_, i) => graph.filter(t => t.wave === i + 1).length))
log(`${graph.length} tasks in ${waves} waves, widest wave ${widest} (at most 8 agents run at once)`)

phase('Write')
await agent(
  `Write docs/tickets/${ID}/PLAN.md for ticket ${ID} (${ticket.title}) with the status line "**Plan:** 🟡 Awaiting approval", ` +
  `this summary: ${JSON.stringify(plan.summary)}, the assumptions ${JSON.stringify([...ticket.assumptions, ...plan.assumptions])}, ` +
  `the waves table, and this task graph in a json block, exactly: ${JSON.stringify(graph)}. ` +
  `Then append to docs/tickets/${ID}/PROGRESS.md: "Plan written: ${graph.length} tasks, ${waves} waves, awaiting approval" (⏳).`,
  { agentType: 'scribe', label: `scribe ${ID}` },
)

return {
  ticket: ID,
  title: ticket.title,
  tasks: graph.length,
  waves,
  widestWave: widest,
  assumptions: [...ticket.assumptions, ...plan.assumptions],
  next: `Review docs/tickets/${ID}/PLAN.md, change its status to "**Plan:** 🟢 Approved", then run /ticket-run ${ID}`,
}
