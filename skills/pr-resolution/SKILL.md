---
name: pr-resolution
version: 0.2.0
description: Resolve PR blockers through evidence-backed repair, verification, and safe handoff.
---

# PR Resolution

Use `$goal-loop-runner` to own the final state: a reviewable, merge-ready PR or a precisely evidenced blocker.
Read branch status, diff, failing checks, review comments, and repository instructions before changing code.
After each repair, run the smallest relevant test, build, lint, review, or CI gate and inspect the diff.

Do not repeat an unchanged failing command. Record the failed hypothesis, evidence, different repair, and
gate result. Use Playwright Extension MCP exclusively for any GitHub, preview, or browser interaction; prefer
semantic CLI/API operations when a browser is unnecessary. Do not enter credentials, bypass branch protection,
or merge without authority.

Report the PR, passed/failed gates, evidence, next action, and any blocked prerequisite. Promote a lesson to
shared guidance only after later validation proves it reusable.

## Evolution Contract

Task-local observations stay in state. Shared updates require a trigger, exact change, evidence, scope, and
rollback condition and must preserve approval boundaries.

