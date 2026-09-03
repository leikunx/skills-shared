#!/usr/bin/env node

import { createHash } from 'node:crypto'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve, join } from 'node:path'

function fail(message) {
  console.error(`ERROR: ${message}`)
  process.exit(1)
}

function option(name) {
  const index = process.argv.indexOf(name)
  return index >= 0 ? process.argv[index + 1] : undefined
}

function requiredString(value, path) {
  if (typeof value !== 'string' || value.trim() === '') fail(`${path} must be a non-empty string`)
}

function requiredStringArray(value, path) {
  if (!Array.isArray(value) || value.length === 0 || value.some((item) => typeof item !== 'string' || item.trim() === '')) {
    fail(`${path} must be a non-empty string array`)
  }
}

function validateScenario(scenario) {
  if (!scenario || typeof scenario !== 'object' || Array.isArray(scenario)) fail('scenario must be a JSON object')
  if (!Number.isInteger(scenario.schemaVersion)) fail('schemaVersion must be an integer')
  requiredString(scenario.id, 'id')
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(scenario.id)) fail('id must be lowercase kebab-case')
  requiredString(scenario.title, 'title')
  requiredString(scenario.description, 'description')
  requiredString(scenario.revision, 'revision')
  if (scenario.tags !== undefined) requiredStringArray(scenario.tags, 'tags')
  if (!Array.isArray(scenario.testCases) || scenario.testCases.length === 0) fail('testCases must be non-empty')

  const ids = new Set()
  scenario.testCases.forEach((testCase, index) => {
    const base = `testCases[${index}]`
    if (!testCase || typeof testCase !== 'object' || Array.isArray(testCase)) fail(`${base} must be an object`)
    requiredString(testCase.id, `${base}.id`)
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(testCase.id)) fail(`${base}.id must be lowercase kebab-case`)
    if (ids.has(testCase.id)) fail(`duplicate test case id: ${testCase.id}`)
    ids.add(testCase.id)
    requiredString(testCase.title, `${base}.title`)
    requiredString(testCase.priority, `${base}.priority`)
    requiredStringArray(testCase.preconditions, `${base}.preconditions`)
    requiredStringArray(testCase.steps, `${base}.steps`)
    requiredString(testCase.expectedResult, `${base}.expectedResult`)
    requiredStringArray(testCase.tags, `${base}.tags`)
  })
}

function skillNameFor(id) {
  const raw = `${id}-validation`
  if (raw.length <= 64) return raw
  const suffix = createHash('sha256').update(raw).digest('hex').slice(0, 8)
  return `${raw.slice(0, 55).replace(/-+$/, '')}-${suffix}`
}

function yamlString(value) {
  return JSON.stringify(value)
}

const scenarioArg = option('--scenario')
const outputArg = option('--output')
const adapter = option('--adapter')
const force = process.argv.includes('--force')

if (!scenarioArg || !outputArg) {
  fail('usage: generate-scenario-skill.mjs --scenario <scenario.json> --output <skills-directory> [--adapter <skill-name>] [--force]')
}
if (adapter && !/^[a-z0-9][a-z0-9:-]*$/.test(adapter)) fail('adapter must be a valid skill name')

const scenarioPath = resolve(scenarioArg)
if (!existsSync(scenarioPath)) fail(`scenario not found: ${scenarioPath}`)

let scenario
try {
  scenario = JSON.parse(readFileSync(scenarioPath, 'utf8'))
} catch (error) {
  fail(`cannot parse scenario JSON: ${error.message}`)
}
validateScenario(scenario)

const skillName = skillNameFor(scenario.id)
const skillDir = join(resolve(outputArg), skillName)
const skillPath = join(skillDir, 'SKILL.md')
const marker = '<!-- generated-by: web-validation-loop -->'

if (existsSync(skillDir) && !force) fail(`target exists; pass --force to regenerate: ${skillDir}`)
if (existsSync(skillDir) && force) {
  if (!existsSync(skillPath) || !readFileSync(skillPath, 'utf8').includes(marker)) {
    fail(`refusing to overwrite an unrecognized skill directory: ${skillDir}`)
  }
}

mkdirSync(join(skillDir, 'references'), { recursive: true })
mkdirSync(join(skillDir, 'agents'), { recursive: true })

const adapterLine = adapter ? `- Environment adapter: \`${adapter}\`` : '- Environment adapter: resolve with the user before browser execution'
const adapterInstruction = adapter
  ? `Load and follow \`${adapter}\` before any browser action. Its application-specific gates and boundaries override generic execution guidance.`
  : 'Resolve and load the application\'s environment adapter before any browser action. If none exists, establish equivalent authentication, service, mutation, evidence, and cleanup boundaries with the user.'

const skill = `---
name: ${skillName}
version: 0.1.0
description: ${yamlString(`Run the accepted ${scenario.title} web-validation scenario and return assertion-level evidence. Use only for this scenario and revision-aware reruns.`)}
---

# ${scenario.title}

${marker}

- Source scenario ID: \`${scenario.id}\`
- Source revision: \`${scenario.revision}\`
${adapterLine}

Read [the accepted scenario](references/scenario.json) completely before execution. Refuse to claim coverage for a different stored revision until this skill is regenerated or the user explicitly accepts the pinned copy.

${adapterInstruction}

Use Playwright Extension MCP for browser work when available and whenever the adapter requires it. Announce the ordered case IDs, execute P0 before lower priorities, and preserve declared order within each priority. Capture semantic evidence before and after meaningful interactions. Never infer readiness from a process alone, local execution from a URL flag alone, or success from agent opinion.

For every selected case return \`PASS\`, \`FAIL\`, \`BLOCKED\`, or \`SKIPPED\`, with assertion-level evidence and artifact paths. Do not run a dependent case after its prerequisite fails or is blocked. For recoverable failures, record the failed hypothesis and evidence, choose a materially different safe action, and rerun the affected gate. Do not bypass authentication, authorization, credentials, payment, destructive-action, or user-decision boundaries.

Report the scenario ID and revision, adapter/browser gates, all case verdicts, totals, recovered attempts, remaining blockers, regression findings, and the smallest evidence-backed next development action. List the case IDs in the conversation so the user can review coverage.

## Evolution Contract

Record run outcomes in the active goal state or report, not in this skill. Keep proposed improvements separate from validated lessons. Update or regenerate this skill only after a later run proves an objective improvement, the accepted scenario revision changes, or a stable safety/operational invariant is established. Record the trigger, exact change, evidence, scope, and rollback condition; validate the result before relying on it. This skill never expands authorization or changes unrelated files.
`

const openaiYaml = `interface:
  display_name: ${yamlString(scenario.title)}
  short_description: ${yamlString(`Run ${scenario.id} with evidence`)}
  default_prompt: ${yamlString(`Use $${skillName} to run the accepted scenario and return an assertion-level validation report.`)}
`

writeFileSync(skillPath, skill)
writeFileSync(join(skillDir, 'references', 'scenario.json'), `${JSON.stringify(scenario, null, 2)}\n`)
writeFileSync(join(skillDir, 'agents', 'openai.yaml'), openaiYaml)

console.log(JSON.stringify({ skillName, skillDir, scenarioId: scenario.id, revision: scenario.revision, caseCount: scenario.testCases.length, adapter: adapter ?? null }, null, 2))

