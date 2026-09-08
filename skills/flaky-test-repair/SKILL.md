---
name: flaky-test-repair
description: Diagnose and repair intermittently failing tests using repeated and cross-run evidence. Use when a test passes and fails without a matching product change; do not use for deterministic regressions, broad CI outages, or merely rerunning a failed job.
---

# Flaky Test Repair

Turn an intermittent failure into a classified, reproducible cause and the smallest behavior-preserving correction.

## Establish that the failure is flaky

Read applicable repository instructions and the test runner configuration. Build a failure corpus from available local runs and CI history without fetching unnecessary full logs. Preserve test identifier, revision, branch, environment, seed, timing, failure signature, and whether the same revision later passed.

Read [classification.md](references/classification.md) before deciding what to repair. A single failure with no retry or cross-run evidence is `insufficient`, not proof of flakiness.

Separate these outcomes:

- `flaky`: materially identical code can pass or fail because of nondeterministic test or product behavior;
- `deterministic-regression`: failure tracks a product or test change;
- `infrastructure`: runner, dependency, capacity, network, port, or service setup failed;
- `insufficient`: evidence cannot distinguish the cases.

Report non-flaky outcomes with their evidence and route them to the appropriate owner. Do not disguise infrastructure instability with test retries.

## Reproduce and isolate

Run the narrowest test target under conditions that can expose the suspected cause: repeated execution, randomized order or seed, constrained concurrency, alternate timing, or isolated/shared process state. Change one stress dimension at a time and retain the exact reproducible command.

Inspect the test and the production boundary together. Common causes include leaked global state, incomplete cleanup, unordered collections, real clocks or random sources, unawaited background work, port collisions, event races, and assertions made before a state transition is observable.

## Repair

Prefer a fix that removes nondeterminism:

- wait on an observable condition or event with a bounded deadline;
- inject time, randomness, or external I/O;
- give each test isolated state and unique resources;
- await and clean up spawned work;
- assert behavior at a stable public boundary.

Do not lengthen arbitrary sleeps, add blind retries, weaken assertions, quarantine the test, or raise global timeouts unless the evidence shows that policy is the desired behavior. When production code owns the race, repair production code and add a deterministic regression test rather than masking it in the test.

## Verify

Rerun the exact reproducer enough times and under the stress condition that previously exposed the failure. Then run the affected test file or package and the repository's relevant lint/type/build gate. Record run counts, seeds or scheduling controls, commands, and results; do not report “stable” without the observed sample.

Review the diff for reduced assertions, hidden retries, new global state, or production behavior changes. Remote CI retries, commits, pushes, and pull requests remain separate actions governed by the user's request and repository instructions.

## Provenance

This skill was independently adapted from general classification and evidence ideas in the private `caifali_microsoft/cowork-engineering-skills` repository at commit `8823967117854eac8d5f53126c05b5574fe5beb1`. Aether, Azure DevOps, fixed pipeline identifiers, and automatic-merge behavior were intentionally removed.

## Evolution Contract

Record task-local outcomes in the active goal state, not in this skill. Keep proposed improvements separate from validated lessons. Update this skill or its references only after a later run proves an objective improvement or establishes a stable safety or operational invariant. For every self-update, record the trigger, exact change, evidence, scope, and rollback condition, then validate the changed skill before relying on it. This contract does not expand authorization or permit unrelated changes.
