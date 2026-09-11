---
name: validation-web-loop
description: Turn stored web-validation scenarios into scenario-specific skills and run evidence-gated browser feedback loops. Use when authoring a scenario, materializing its executor, or validating a web application from scenario configuration; do not use for unit-only testing.
---

# Web Validation Loop

Use a stored scenario as the contract between test design, browser execution, and development feedback. Keep application-specific authentication, startup, mutation, and cleanup rules in an environment adapter skill rather than embedding them here.

Read [the scenario and report contract](references/scenario-contract.md) before authoring, generating, or executing a scenario. Before browser execution, also read [the browser execution contract](references/browser-execution-contract.md).

## Choose the mode

### Author or revise a scenario

Use the available `validation_scenario_*` MCP tools. For a new scenario, call `validation_scenario_find_related` first, inspect the closest results, then create explicit cases that cover the applicable primary flow, validation and error states, authorization boundary, loading or empty states, persistence, accessible outcomes, and regression risks. Obey the create tool's required case count and schema.

For an update, call `validation_scenario_get` first and supply its exact revision to one `validation_scenario_update` operation. On a revision conflict, read again and reconcile; never overwrite newer content. Scenario authoring grants no permission to run a browser or mutate application data.

Tell the user which cases were created or changed, why they cover the main risks, and the resulting path, revision, and count.

### Materialize a scenario-specific skill

Run the deterministic generator with the accepted scenario file and a destination directory:

```text
node <this-skill-directory>/scripts/generate-scenario-skill.mjs --scenario <scenario.json> --output <skills-directory> [--adapter <environment-adapter-skill>]
```

The generator names executors `validation-<scenario-id>`, validates required fields and unique case IDs, copies the accepted scenario into the generated skill, and refuses to overwrite an existing directory unless `--force` is supplied. Use `--force` only when the existing directory carries this generator's current or legacy marker and the user requested regeneration. Review scenario contents before distributing a generated skill because task-local URLs or test data may be private.

Validate the generated skill structurally before using it. A generated skill is a scenario executor, not new authority: it inherits the scenario's and adapter's boundaries.

### Execute and loop

1. Read the scenario and its revision. Load the declared environment adapter and follow its preflight, authentication, local-service, mutation, evidence, and cleanup rules before browser interaction.
2. Check whether Playwright Extension MCP is available. Use it for the initial and subsequent browser actions when available. Use another browser surface only when the user requested it, the extension is unavailable, or it lacks a required capability; record the reason in the report.
3. Acquire one exclusive browser-writer lease for the connected page. Serialize navigation and interaction cases; parallelize only work that cannot mutate browser state. Record any intentional continuation between cases as an explicit dependency.
4. Announce the selected cases and prerequisites. Execute P0 before lower priorities, preserving declared order within a priority. Do not execute a dependent case after its prerequisite is `BLOCKED` or `FAIL`; classify it accurately.
5. Capture an accessibility snapshot before each meaningful interaction and objective evidence after it. Prefer role, accessible name, and stable test-id locators. Select additional evidence surfaces only when the application behavior needs them: bounded console/network diagnostics, adapter-defined streaming events, screenshots, or a persisted-artifact re-read. Never store secrets or raw private payloads.
6. Return an assertion-level result for every selected case: `PASS`, `FAIL`, `BLOCKED`, or `SKIPPED`. Account for browser/tool crashes as unexecuted evidence rather than product failures. A process existing, a URL containing a local flag, or the agent's opinion is not proof.
7. For a recoverable failure, record `hypothesis -> evidence -> verdict -> changed next action`, restore a known browser state or open a fresh page, and rerun only the affected gate and dependent cases. Do not repeat an unchanged failure or reuse observations from a changed environment.
8. Stop only when the selected cases have terminal results and the final readiness/report gate passes, or when an adapter-defined external prerequisite persists. Never bypass authentication, authorization, payment, destructive-action, or user-decision boundaries to keep looping.

Return the scenario ID/revision, environment and browser fingerprint, every case verdict with evidence, totals, unresolved blockers, regression findings, and the smallest next development action. When a prior report has the same scenario revision, assertion contract, adapter, and environment fingerprint, compare case IDs and call out regressions and recoveries; otherwise mark the baseline non-comparable. In conversation, list the tested case IDs before the summary so users can review coverage.

## Evolution Contract

Record task-local outcomes in the active goal state or run report, not in this skill. Keep proposed improvements separate from validated lessons. Update this skill or its references only after a later run proves an objective improvement or a stable safety/operational invariant. For every self-update, record the trigger, exact change, evidence, scope, and rollback condition in the goal and [evolution log](references/evolution-log.md), then validate the changed skill before relying on the new rule. This skill never expands authorization or changes unrelated files.
