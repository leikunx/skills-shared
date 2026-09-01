---
name: loop
description: "Run a task as an iterative work-and-verify loop until a stated success or safe stop condition is reached. Use when the user asks to keep checking, retrying, monitoring, or looping on work; not for a one-shot task."
---

# Loop

Turn the user's request into an observable loop. The loop must have a target, a check that determines its current state, and a stopping condition.

1. State the target and the condition that proves completion. If an indefinite loop is requested, ask for a duration, maximum attempts, or another safe stopping condition before performing actions with external effects.
2. Take the next useful action, then verify its result from authoritative state (tests, process status, page state, command output, or the requested external system).
3. If incomplete, determine whether another action can materially improve the state. Perform it and re-check. Do not merely repeat an action that has no path to a changed result.
4. For a wait or monitoring loop, poll the specific live process, job, page, or resource at a reasonable interval. Report meaningful changes and completion; do not claim progress solely because time passed.
5. Stop when the completion condition is proven, a requested limit is reached, or further action needs new user authorization. Summarize the final state and any remaining action needed.

Use goal tracking when it is available and the task is multi-step or long-running. Keep the original objective intact and update the goal only when completion is proven or the platform's blocked criteria are satisfied.

This skill is an iterative workflow, invoked as `$loop`; it does not add a native `/loop` command, background scheduler, or persistent timer to Codex. For recurring unattended runs, use an external scheduler that launches `codex exec` with a bounded prompt and writes results to a chosen location.
