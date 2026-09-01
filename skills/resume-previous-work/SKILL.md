---
name: resume-previous-work
description: Find a recorded unfinished task from prior Codex goals or sessions, validate its current state, and safely resume the next supported action.
---

# Resume Previous Work

Use this skill when the user asks to continue, recover, or find work from an earlier Codex session.

1. Check the active goal first, then inspect the current workspace's `.codex/goals/**/STATE.md` files. Classify each relevant record as complete, blocked, or resumable from its `Current status` and `Next smallest action`.
2. If the workspace records do not identify the task, search the local Codex history for a narrow set of terms from the user's request. Treat history as a lead, not proof; do not expose unrelated conversation content.
3. Before resuming, inspect the current repository, service, process, browser, or remote state that the recorded next action depends on. Do not repeat a stale action merely because it appears in a state file.
4. Preserve the original task's authorization, safety boundaries, and verification gate. Ask only when the recovered record lacks a material decision or external permission.
5. Record the classification, fresh evidence, selected next action, and any changed blocker in the active goal state. Do not claim a recovered task is complete without its original gate.

If all recovered work is complete or externally blocked, report the evidence and the smallest condition that would permit continuation.
