// Runs .claude/workflows/ticket-run.js with stand-in agents, so that the tests see what the workflow does.
// Usage: node run_workflow.mjs <scenario.json>. The scenario holds "args" and "rules": each rule matches an agent call by
// agentType, a part of its label and a part of its prompt, and gives its reply, "times" times (every time without it).
// A call no rule matches gets the default reply of its agent type. Prints {result, calls, logs} as JSON.
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const script = readFileSync(resolve(here, '../../../.claude/workflows/ticket-run.js'), 'utf8').replace(/^export /m, '')
const scenario = JSON.parse(readFileSync(process.argv[2], 'utf8'))
const WORKER = { status: 'done', worktree: '', files_changed: [], checks: [], assumptions: [], decisions: [], blocked_by: [] }
const DEFAULTS = {
  runner: { exit_code: 0, output: [] },
  integrator: { integrated: [], blocked: [], tree: 'abc1234', home: '/home/swarm', conflicts_resolved: [] },
  verifier: { passed: true, failures: [], not_applicable: [] },
  reviewer: { verdict: 'approve', findings: [], note: 'Approved.', assumptions_accepted: [], resolved: [] },
}
const calls = []
const logs = []
const matches = (rule, prompt, opts) =>
  (!rule.agentType || rule.agentType === opts.agentType) &&
  (!rule.label || String(opts.label || '').includes(rule.label)) &&
  (!rule.prompt || prompt.includes(rule.prompt)) &&
  (rule.times === undefined || rule.times > 0)
async function agent(prompt, opts = {}) {
  calls.push({ agentType: opts.agentType || '', label: opts.label || '', prompt })
  const rule = scenario.rules.find(r => matches(r, prompt, opts))
  if (rule) {
    if (rule.times !== undefined) rule.times -= 1
    return structuredClone(rule.reply)
  }
  if (opts.label && opts.label.startsWith('gate')) return structuredClone(scenario.gate)
  if (DEFAULTS[opts.agentType]) return structuredClone(DEFAULTS[opts.agentType])
  return opts.schema ? structuredClone(WORKER) : ''
}
const parallel = async thunks => Promise.all(thunks.map(t => t().catch(() => null)))
const run = new Function('agent', 'parallel', 'phase', 'log', 'args', `return (async () => {${script}\n})()`)
const result = await run(agent, parallel, () => {}, message => logs.push(message), scenario.args)
console.log(JSON.stringify({ result, calls, logs }))
