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
// L-31: a step that runs one deterministic command goes to the runner agent, which only runs that command and reports
// its exit code and output. The workflow decides from them, never from an agent's reading: the verifier, whose own job
// is running checks.py, once returned the ticket's test failures as a refusal of the start rule.
const RUN = {
  type: 'object',
  properties: { exit_code: { type: 'integer' }, output: { type: 'array', items: { type: 'string' } } },
  required: ['exit_code', 'output'],
}
// L-35: the runner gets one command, with its folder as a cd in front, never a sentence asking it to find the folder.
// L-40: the Bash tool shows no exit code when a command succeeds, so the runner guessed 1 from a warning. The command
// prints its own exit code as its last line, and that number decides, never the runner's reading.
const EXIT_MARK = 'SWARM_EXIT_CODE='
async function runExactly(dir, command, expect, opts) {
  const line = `${dir ? `cd ${JSON.stringify(dir)} && ` : ''}${command}; echo "${EXIT_MARK}$?"`
  const ran = await agent(
    `Run exactly this one command, and nothing else: ${line}\nReport every line it printed, the last one included, and in exit_code the number after ${EXIT_MARK}.`,
    { agentType: 'runner', schema: RUN, ...opts },
  )
  if (!ran) return null
  const marked = ran.output.map(l => String(l).match(/SWARM_EXIT_CODE=(\d+)/)).filter(Boolean).pop()
  const exit = marked ? Number(marked[1]) : ran.exit_code
  const output = ran.output.filter(l => !String(l).includes(EXIT_MARK))
  if (marked && exit !== ran.exit_code) log(`Runner reported exit ${ran.exit_code}, the command printed ${exit}: ${exit} decides (L-40)`)
  const passed = exit === expect.exit && (!expect.quiet || output.length === 0)
  return { passed, problems: output, exit_code: exit }
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
// TKT-23: a ticket already done (merged, or its issue closed on GitHub) or finished (its pull request open) is never
// planned again: tickets.py holds the one definition of done.
const notDone = await runExactly('', `python3 .claude/scripts/tickets/tickets.py done --ticket ${ID}`, { exit: 1, quiet: true },
  { label: `done check ${ID}` },
)
if (!notDone || !notDone.passed) {
  return { ticket: ID, stopped: (notDone && notDone.problems.join(' ')) || 'tickets.py done did not report', next: 'Nothing to plan.' }
}
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
const checkTicket = () => runExactly('', `python3 .claude/skills/ticket/scripts/check_ticket.py ${ID}`,
  { exit: 0, quiet: true }, { label: `check TICKET.md ${ID}` },
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
// L-46: a scribe once put links after the status, and the plan could not be approved. The status line is given exactly,
// alone on its line.
const STATUS_LINE = '**Plan:** 🟡 Awaiting approval'
const STATUS_RULE = `The status line is exactly "${STATUS_LINE}", alone on its own line, with nothing before or after it on that line (no link, no other field); put anything else on another line.`
const written = await agent(
  `Write docs/tickets/${ID}/PLAN.md for ticket ${ID} (${ticket.title}). ${STATUS_RULE} ` +
  `this summary: ${JSON.stringify(plan.summary)}, the assumptions ${JSON.stringify([...ticket.assumptions, ...plan.assumptions])}, ` +
  `then a "## Task graph" heading and this task graph in a json block, exactly: ${JSON.stringify(graph)}. ` +
  `Then run python3 .claude/scripts/tickets/plan.py render --ticket ${ID}, which pretty-prints the json block and writes from it the waves table, ` +
  `the dependency graph and one section per task for the person; it must print nothing. Then append to the Events table of docs/tickets/${ID}/PROGRESS.md: "Plan written: ${graph.length} tasks, ${waves} waves" (⏳ Awaiting approval), ` +
  `Then run python3 .claude/scripts/tickets/ticket_refs.py sync --ticket ${ID}, which copies the specification references of TICKET.md into PLAN.md and PROGRESS.md, ` +
  `and python3 .claude/scripts/reports/progress.py timings --ticket ${ID} --write. ` +
  `Then run python3 .claude/scripts/github/board.py move --ticket ${ID} --status planned, which moves its card to 📝 Planned on the GitHub board (TKT-17); ` +
  `if it fails because gh is missing or offline, go on. ` +
  `Last, run python3 .claude/scripts/tickets/ticket_refs.py check --ticket ${ID} and python3 .claude/scripts/tickets/plan.py check --ticket ${ID}, ` +
  `and return in problems every line they print (none when all is well).`,
  { agentType: 'scribe', schema: WRITE_SCHEMA, label: `scribe ${ID}` },
)
const problems = (written && written.problems) || ['the scribe returned no result']
if (problems.length) log(`PLAN.md, PROGRESS.md or TICKET.md fails its checks: ${problems.join(' | ')}`)

const checkPlan = () => runExactly('', `python3 .claude/skills/ticket/scripts/check_plan.py ${ID}`,
  { exit: 0, quiet: true }, { label: `check PLAN.md ${ID}` },
)
let planVerdict = await checkPlan()
let planCheck = 'passed'
if (!planVerdict || !planVerdict.passed) {
  // L-46: a failed plan check goes back to the scribe once, before the workflow ends.
  const first = (planVerdict && planVerdict.problems) || ['the runner returned no result']
  log(`PLAN.md fails check_plan.py, back to the scribe once: ${first.join(' | ')}`)
  await agent(
    `Fix docs/tickets/${ID}/PLAN.md so that python3 .claude/skills/ticket/scripts/check_plan.py ${ID} prints nothing. ` +
    `Its problems: ${JSON.stringify(first)}. ${STATUS_RULE} A count of tasks or waves in the summary is the task graph's: ` +
    `${graph.length} tasks in ${waves} waves. Never change the json block: a problem in the task graph itself is left for the person. ` +
    `Then run python3 .claude/scripts/tickets/plan.py render --ticket ${ID}. Change nothing else.`,
    { agentType: 'scribe', schema: WRITE_SCHEMA, label: `scribe plan fix ${ID}` },
  )
  planVerdict = await checkPlan()
}
if (!planVerdict || !planVerdict.passed) {
  const planProblems = (planVerdict && planVerdict.problems) || ['the runner returned no result']
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
  // L-47: every running ticket shares the main checkout on feature/tickets (TKT-16); a group is approved once (TKT-20).
  next: planCheck === 'passed'
    ? `Review docs/tickets/${ID}/PLAN.md, then approve it: change its status line to "**Plan:** 🟢 Approved", or, for a group, run python3 .claude/scripts/tickets/tickets.py approve <refs> once for all its plans (TKT-20). ` +
      `Then run /ticket-run ${ID}, or /issue-run <refs> for the group: every running ticket works in the main checkout, on the shared branch feature/tickets, beside the others (TKT-16).`
    : `PLAN.md fails check_plan.py (see planCheck): fix it, or run /ticket-plan ${ID} again, before it can be approved.`,
}
