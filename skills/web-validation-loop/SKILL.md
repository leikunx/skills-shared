---
name: web-validation-loop
version: 0.1.0
description: Turn stored web-validation scenarios into scenario-specific skills and run evidence-gated browser feedback loops. Use when authoring a scenario, materializing its executor, or validating a web application from scenario configuration; do not use for unit-only testing.
---

# Web Validation Loop

Use a stored scenario as the contract between test design, browser execution, and development feedback. Keep application-specific authentication, startup, mutation, and cleanup rules in an environment adapter skill rather than embedding them here.

Read [the scenario and report contract](references/scenario-contract.md) before authoring, generating, or executing a scenario.

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

The generator validates required fields and unique case IDs, copies the accepted scenario into the generated skill, and refuses to overwrite an existing directory unless `--force` is supplied. Use `--force` only when the existing directory carries this generator's marker and the user requested regeneration. Review scenario contents before distributing a generated skill because task-local URLs or test data may be private.

Validate the generated skill structurally before using it. A generated skill is a scenario executor, not new authority: it inherits the scenario's and adapter's boundaries.

### Execute and loop

1. Read the scenario and its revision. Load the declared environment adapter and follow its preflight, authentication, local-service, mutation, evidence, and cleanup rules before browser interaction.
2. Check whether Playwright Extension MCP is available. Use it for the initial and subsequent browser actions when available. Use another browser surface only when the user requested it, the extension is unavailable, or it lacks a required capability; record the reason in the report.
3. Announce the selected cases and prerequisites. Execute P0 before lower priorities, preserving declared order within a priority. Do not execute a dependent case after its prerequisite is `BLOCKED` or `FAIL`; classify it accurately.
4. Capture an accessibility snapshot before each meaningful interaction and objective evidence after it. Prefer role, accessible name, and stable test-id locators. Record route/state assertions, relevant network or console evidence, and artifact paths without secrets.
5. Return an assertion-level result for every selected case: `PASS`, `FAIL`, `BLOCKED`, or `SKIPPED`. A process existing, a URL containing a local flag, or the agent's opinion is not proof.
6. For a recoverable failure, record `hypothesis -> evidence -> verdict -> changed next action`, take a materially different safe action, and rerun only the affected gate and dependent cases. Do not repeat an unchanged failure.
7. Stop only when the selected cases have terminal results and the final readiness/report gate passes, or when an adapter-defined external prerequisite persists. Never bypass authentication, authorization, payment, destructive-action, or user-decision boundaries to keep looping.

Return the scenario ID/revision, environment and browser gates, every case verdict with evidence, totals, unresolved blockers, regression findings, and the smallest next development action. In conversation, list the tested case IDs before the summary so users can review coverage.

## Evolution Contract

Record task-local outcomes in the active goal state or run report, not in this skill. Keep proposed improvements separate from validated lessons. Update this skill or its references only after a later run proves an objective improvement or a stable safety/operational invariant. For every self-update, record the trigger, exact change, evidence, scope, and rollback condition, then validate the changed skill before relying on the new rule. This skill never expands authorization or changes unrelated files.
