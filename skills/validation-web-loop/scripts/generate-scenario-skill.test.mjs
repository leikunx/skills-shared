import test from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

test('generated executor carries browser ownership and evidence boundaries', (t) => {
  const root = mkdtempSync(join(tmpdir(), 'scenario-skill-test-'))
  t.after(() => rmSync(root, { recursive: true, force: true }))
  const output = join(root, 'skills')
  mkdirSync(output)
  const scenario = {
    schemaVersion: 1,
    id: 'restore-flow',
    title: 'Restore flow',
    description: 'Verify a saved draft survives a reload.',
    revision: 'r1',
    tags: ['persistence'],
    testCases: [{
      id: 'reload-draft',
      title: 'Reload a saved draft',
      priority: 'P0',
      preconditions: ['A disposable draft exists.'],
      steps: ['Reload the page.', 'Open the same draft.'],
      expectedResult: 'The draft identity and content are unchanged.',
      tags: ['restore'],
    }],
  }
  const scenarioPath = join(root, 'scenario.json')
  writeFileSync(scenarioPath, JSON.stringify(scenario))
  const generator = fileURLToPath(new URL('./generate-scenario-skill.mjs', import.meta.url))
  const stdout = execFileSync(process.execPath, [generator, '--scenario', scenarioPath, '--output', output, '--adapter', 'example-adapter'], { encoding: 'utf8' })
  const generated = JSON.parse(stdout)
  assert.equal(generated.skillName, 'validation-restore-flow')
  assert.equal(generated.skillDir, join(output, generated.skillName))
  const skill = readFileSync(join(generated.skillDir, 'SKILL.md'), 'utf8')
  assert.match(skill, /^name: validation-restore-flow$/m)
  const accepted = JSON.parse(readFileSync(join(generated.skillDir, 'references', 'scenario.json')))
  assert.equal(accepted.testCases[0].id, 'reload-draft')
  assert.match(skill, /exclusive browser-writer resource/)
  assert.match(skill, /denial or cancellation case/)
  assert.match(skill, /label it non-comparable/)
  assert.doesNotMatch(skill, /internal-host|product-specific-event|fixed agent/i)

  const args = [generator, '--scenario', scenarioPath, '--output', output, '--adapter', 'example-adapter']
  assert.throws(() => execFileSync(process.execPath, args, { stdio: 'pipe' }), /target exists/)
  const skillPath = join(generated.skillDir, 'SKILL.md')
  writeFileSync(skillPath, skill.replace('generated-by: validation-web-loop', 'generated-by: web-validation-loop'))
  execFileSync(process.execPath, [...args, '--force'], { stdio: 'pipe' })
  assert.equal(readFileSync(skillPath, 'utf8'), skill)
  writeFileSync(skillPath, 'Unrelated authored skill')
  assert.throws(() => execFileSync(process.execPath, [...args, '--force'], { stdio: 'pipe' }), /unrecognized skill directory/)
})
