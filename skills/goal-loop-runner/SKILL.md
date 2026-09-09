---
name: goal-loop-runner
description: "Run a long-horizon task as a goal-driven, stateful, evidence-gated iteration loop. Use for Goal mode, 'continue until done', recurring or unattended pursuit windows, or fuzzy voice-transcribed requests that need a reviewable goal contract."
---

# Goal Loop Runner

Combine Codex goal tracking with a disciplined execution loop. The goal preserves the user’s objective across turns; the loop makes every iteration produce fresh evidence and a useful next decision.

## Turn a natural-language request into a strong Goal

Treat the user's request as natural language, not as a pre-filled Goal contract. Before creating a Goal or taking substantive action, translate it into this six-part draft:

1. **Outcome:** what must be true at completion.
2. **Verification surface:** the concrete evidence that will prove it.
3. **Constraints:** behavior, quality, safety, or compatibility that must not regress.
4. **Boundaries:** permitted files, systems, tools, data, and external actions.
5. **Iteration policy:** how to choose the next smallest experiment after each result.
6. **Blocked stop condition:** when to stop, what evidence to report, and what input or authority would unblock progress.

### Fuzzy or voice-transcribed input preflight

Unless the user explicitly says otherwise, presume their messages are speech-to-text transcriptions. Before acting,
silently infer the most coherent intended meaning by resolving obvious homophones, repeated syllables, punctuation
loss, and contextually implausible words against the active goal and available evidence. Treat that inference as an
assumption, not as a license to change the user's authority, desired outcome, verification method, or risk boundary.
When a materially different interpretation would change one of those things, surface the alternatives and ask one
narrow clarifying question. Retain confirmed transcription corrections as task facts in the goal state; promote only
stable, user-established conventions to reusable guidance.

Treat an input as **fuzzy** when speech disfluencies, repetitions, fragments, vague references (such as “that thing” or “the previous goal”), missing success criteria, or conflicting directions leave any of the six parts materially uncertain. Do not mistake informal wording alone for uncertainty; infer ordinary implementation details when that does not change authority, risk, the verification method, or the intended outcome.

For fuzzy input, before creating a Goal or taking substantive action, show the user the six-part draft in the first progress update. Mark every material inference as `Assumption:`. Then perform and show a concise **Contract review** with one finding for each element:

1. Does the Outcome describe an observable end state rather than an activity?
2. Can the Verification surface produce evidence independent of the agent's opinion?
3. Do Constraints protect the important safety, quality, and compatibility requirements?
4. Do Boundaries name the allowed systems/actions and avoid silently expanding authority?
5. Does the Iteration policy choose a smallest evidence-producing next action and avoid unchanged retries?
6. Does the Blocked stop condition name the evidence, missing input, or authority needed to proceed?

End the review with `Decision: proceed`, `Decision: proceed with stated assumptions`, or `Decision: clarification required`. A self-review checks the contract's usefulness; it is never proof that the eventual outcome is correct.

If a review finding is weak but can be safely repaired, revise the draft once using explicit assumptions and review the revision. Ask one narrow clarifying question only if a remaining weakness would materially change the objective, proof method, authority, safety risk, or external impact. Until then, do not create a Goal or take substantive action. For a sufficiently concrete request, display the same compact contract but keep the review proportional: an itemized review is needed only when an assumption or material tradeoff needs the user's confirmation.

State the proposed contract concisely in the first progress update. Do not ask about details that can be safely discovered or reasonably assumed; ask only when a missing choice would materially alter the outcome, verification method, authority, or risk. Once the contract is sufficiently concrete, create the Goal and copy the six parts and the Contract review decision into its state file.

Use this compact form when presenting a draft:

```text
Outcome: ...
Verified by: ...
Constraints: ...
Boundaries: ...
Iteration: ...
Blocked when: ...
```

## Establish the contract

Before the first substantive action, establish:

- **Objective:** preserve the active Codex goal if present; otherwise state a concise proposed objective.
- **Done condition:** a concrete result plus an objective gate wherever possible.
- **State file:** use the user-named path; otherwise `.codex/goals/<goal-slug>/STATE.md` in the task workspace. Never reuse a state file belonging to another objective.
- **Limits:** attempts, duration, cost/token budget when supplied, and approval boundaries.

Create the state file from [the state template](references/state-template.md) when needed. At the start of each iteration, read it and the applicable project instructions. At the end, record only facts: action, outcome, evidence, blockers, and the next action.

## Round packet and checkpoint trust

Start every iteration by reconstructing a compact round packet from the original objective and active contract, the latest accepted checkpoint and its evidence, remaining work, relevant failure or rejection evidence, and authoritative user amendments. Do not use a growing raw transcript as task state. Raw trajectories, tool logs, executor claims, partial output, and timed-out work may help diagnosis, but they are not accepted progress by themselves.

Keep attempt, verification, and checkpoint decisions distinct:

1. **Attempt:** perform one bounded action that targets one dominant state change.
2. **Verification:** inspect the real file, application, browser, service, or other final-state carrier against the original contract and the action's gate. Treat the action report only as a claim.
3. **Checkpoint:** promote only independently supported facts and artifacts into accepted state. Put failed, ambiguous, contaminated, or not-yet-verified output under `Untrusted/rejected` with the evidence needed for recovery; never overwrite the last accepted checkpoint with it.

For complex or consequential work, prefer a separate reviewer or verifier when available. Otherwise perform a dedicated verification pass that makes no task-state mutations. Reconstruct the important acceptance constraints from the original request during that pass so contract drift, an incomplete last subtask, or an easier proxy cannot become the completion standard. Goal state and run logs are execution records, not substitutes for the user's requested deliverable.

## Browser automation default

When an iteration requires browser automation, first check whether Playwright Extension MCP tools are available in the current session. When they are available, use Playwright Extension MCP for the initial browser action and collect its result as evidence. Use another browser mechanism only when the user explicitly requests it, the extension is unavailable or disconnected, or the task requires a capability it cannot provide; record that reason in the goal state before continuing.

This preference applies only to browser automation. It does not require browser tooling for non-browser work, bypass user authorization, or replace the task's stated safety boundary.

### Multiple browser profiles and accounts

Treat separate Playwright Extension MCP instances as potentially different authenticated browser profiles. Honor an explicitly requested instance; otherwise select the instance using the task's account or organization context and the user-established mapping in project memory or `AGENTS.md`. Use the project's default when no profile-specific context applies. Do not infer identity from a tool name or assume all instances share a session.

Before an account-sensitive action or external write, verify the live signed-in account and relevant organization or tenant through a read-only check in the selected instance. Record the selected instance, expected identity, and verification evidence in goal state. A remembered mapping is a routing hint, not proof of current authentication. If identity is wrong or uncertain, inspect or recover the intended session; ask only when the target identity cannot be determined from existing context and evidence. A disconnected or signed-out instance does not justify silently substituting another identity, transferring credentials, or changing authorization boundaries. Verify non-browser tool authentication separately when needed; browser sign-in does not establish Git, CLI, or API identity.

Keep exact MCP-instance/profile/account mappings in project memory and task-specific observations in goal state. Shared skill instructions and references must describe this selection policy generally, without embedding local account names, tenant identifiers, or machine-specific mappings. Update project memory when the user establishes a changed mapping.

## Unattended pursuit windows

When the user invokes this skill while saying they will be away, asleep, or unavailable for a stated period, read and follow [the unattended handoff protocol](references/unattended-handoff.md). Before the window begins, present the goal contract and consolidate every material uncertainty that truly requires the user into one clarification message. Record the confirmed window start/end with timezone, recurrence cadence, job/round limit, per-job timeout, exact scheduler command or definition and identifier, non-overlap lease and stale-claim policy, process/log cleanup owner, verification gate, and the same goal-state path. Once the user confirms the contract or explicitly starts the window, do not send blocking questions during it.

Treat the stated period as an instruction to keep pursuing the active goal rather than to end at the first recoverable failure. Use an external scheduler to launch bounded, stateful jobs during that window; the skill itself does not create a daemon or keep an inactive chat turn alive. Prevent overlapping jobs from acting on the same mutable target unless concurrency is explicitly safe. Each job records its scheduler/job id, claims one round with a time-bounded lease, rebuilds the compact round packet, and starts from the last accepted checkpoint rather than from an earlier executor claim. A later job may reclaim a stale lease only after checking that its process or external action is no longer active.

Each unattended job must read the state and first inspect the current browser, process, service, or remote state. After a failure, record the failed hypothesis and try the next materially different safe diagnostic or recovery action in that job. For browser work, examples include rechecking extension connectivity, listing/selecting available tabs, opening a fresh tab, waiting for page readiness, inspecting console/network evidence, and revisiting the relevant authenticated route. Do not repeat an unchanged failed action or stop solely because one page navigation, selector, or process start failed.

Do not ask the user for routine implementation choices during the window when they can be discovered from existing resources or resolved with an already-authorized safe default. For a genuine external prerequisite—such as interactive sign-in, unavailable credentials, multifactor approval, a payment confirmation, or a product decision—do not fabricate an answer or wait inside a job. Record the exact evidence and minimum unblocking action, continue any independent safe work, and let later jobs revalidate the prerequisite until the window ends. Never bypass authentication, fabricate credentials, accept payment terms, or create a charge merely to avoid waiting.

At the end of an unattended window, report the accepted changes, objective-gate evidence, failed and recovered attempts, any remaining external prerequisite, and the next scheduled or user action. Mark a goal blocked only under the normal repeated-blocker policy; an unavailable user during an explicitly requested unattended window is not a reason to abandon safe exploration.

## Evidence-driven self-evolution

For long-running work, improve the workflow through evidence, not unconstrained self-critique. Keep information in three layers:

- **Task state:** The selected `STATE.md` is the short-term memory. Read it each cycle; retain completed evidence, current constraints, blockers, and one credible next action. Remove superseded speculation during periodic compaction.
- **Validated lessons:** Record a lesson only after a later cycle confirms that applying it improved an objective gate. A lesson states the trigger, changed action, and evidence. Keep unvalidated ideas in the iteration log, not durable lessons.
- **Reusable guidance:** Promote a lesson to a project `AGENTS.md` or a skill only when it has proven useful across tasks or is a stable safety/operational invariant. Do not turn a one-off incident into a universal rule.

At the end of each cycle, add a concise reflection only when it changes the next decision: `hypothesis -> observed evidence -> verdict -> changed next action`.

Every 3-5 material cycles, compact the state: preserve the accepted baseline, decisions, artifact paths, open risks, and next action; remove raw tool output and disproven hypotheses. Re-run the applicable gate after any strategy change. Never treat an agent's self-assessment as proof of improvement.

### Evolving skills created during a goal

When this goal produces a new or materially revised skill, give that skill an **Evolution Contract**. Its `SKILL.md` must state that it:

1. records task-local outcomes in the goal state, not in the skill itself;
2. keeps proposed improvements separate from validated lessons;
3. may update its own instructions or references only after a later run proves an objective improvement or a stable safety/operational invariant;
4. records the trigger, exact change, evidence, and rollback condition for every self-update; and
5. validates the changed skill before relying on the new rule in a later run.

Use `references/evolution-log.md` in the generated skill when recurring improvements need a durable audit trail. Do not create that file for a one-shot skill or write to it every cycle. The goal loop remains the governance layer: a skill never expands authorization, changes unrelated files, or treats a failed run as evidence that its own instructions are correct.

## Evolution Contract

This skill records task-local outcomes in the selected goal state, not in this file. Proposed improvements remain provisional until a later run demonstrates an objective improvement or a stable safety/operational invariant. Any self-update must record its trigger, exact change, evidence, scope, and rollback condition in the goal iteration log and [the evolution log](references/evolution-log.md); validate the changed skill before relying on its new rule in a later run. This contract grants no authority to alter unrelated files, expand external actions, or treat self-review as outcome evidence.

## Iteration

For every cycle:

1. Read the active goal, applicable project instructions, and selected state; rebuild the compact round packet from the last accepted checkpoint.
2. Choose the smallest action that can produce one dominant, observable state transition.
3. Execute it within the current round budget, preserving partial output as untrusted evidence if execution fails or times out.
4. Run a distinct verification pass using the defined gate (tests, build, lint, data check, visual check, or another stated proof) against the real final-state carrier and original contract.
5. Inspect the resulting diff or artifact. Promote verified facts into the accepted checkpoint; keep rejected or uncertain output explicitly untrusted.
6. When a failure or blocker changes the approach, record its hypothesis, evidence, and revised action; promote only later-validated lessons.
7. Continue only if a specific next action has a credible path to improvement. Do not repeat an unchanged failed action. If the remaining budget cannot honestly reach the full gate, pursue the most complete verifiable action or report the exact boundary instead of spending the last round on a knowingly insufficient prerequisite.

## Final-deliverable ownership

When the user states the final deliverable, treat it as the agent's execution mandate. The user need not prescribe intermediate attempts, diagnostics, or repairs. Convert the deliverable into a done condition and objective gate, retain it in the goal state, and keep working toward it while a safe, authorized, evidence-backed next action remains.

An unsuccessful action is an **iteration result**, not a terminal response, when its evidence exposes a credible next action. Before taking that action, record the failed hypothesis and evidence; then choose an action that is materially different from the failed one and that either improves the objective or distinguishes between competing causes. Run the relevant objective gate after every repair. Do not ask the user to select ordinary implementation details that can be discovered or safely inferred.

Before reporting final status, check the goal state for an untried, safe, authorized action with a credible path to the done condition. If one exists, take it instead of ending on the failure. Conclude only when one of these conditions holds:

- **Complete:** the final deliverable exists and fresh objective-gate evidence proves its done condition.
- **Blocked:** the same external prerequisite has persisted for three consecutive cycles, or progress requires credentials, external approval, destructive action, or a material product decision. Report the exact evidence, attempts, and minimum unblocking action.
- **User-directed stop:** the user explicitly ends or changes the objective.

### Validated skill evolution during pursuit

After each material failure or recovery, decide whether it exposed a reusable instruction gap. Always record the candidate learning in the goal state. When a later cycle or independent run validates that the changed method improves the relevant gate—or when the user establishes a stable operating requirement—update the smallest relevant skill or reference without waiting for another prompt. Record the trigger, exact change, evidence, scope, and rollback condition in [the evolution log](references/evolution-log.md). Do not modify unrelated skills, and do not promote a one-off workaround or self-assessment as a reusable rule.

## Managed process recovery

When the goal starts a local long-running process such as a watcher, dev server, build, or test runner, the agent owns its lifecycle until the goal ends. Do not wait for the user to notice a failed start.

For every managed process, retain its command, working directory, session/process handle, log path, expected readiness signal, and start time in the goal state. On each relevant cycle, inspect the handle plus an objective readiness signal (for example a listening port, health endpoint, build-complete log entry, or expected artifact).

If it is not ready, diagnose before retrying: inspect stdout/stderr, exit code, process tree, dependency/tool availability, configuration, and the smallest relevant network or credential check. Apply a safe, evidence-supported repair, then re-run the readiness gate. Do not repeat the same start command unchanged after a known failure.

Escalate to the user only when recovery requires credentials, organization membership, a destructive action, external approval, or a product decision. Record the diagnosis, attempted repair, and result in the iteration log. A process merely existing is never proof that it is ready.

### Recovery capture and promotion

When a changed recovery action improves a managed-process gate, add a **provisional recovery record** to the current goal state before continuing. Record only facts: trigger, failed command or action, observed error, exact changed action, readiness evidence, scope/preconditions, and rollback condition. This preserves the usable method for the current goal without claiming that one run establishes a universal rule.

Promote that record to a validated lesson only after a later cycle or independent run applies the changed method and passes the same objective gate. If the method is a stable operational invariant needed by later users, then update the relevant skill or reference with the trigger, exact change, evidence, and rollback condition. Keep one-off tool quirks task-local; do not update a reusable skill merely because a recovery happened once.

Finish only when the done condition and fresh gate evidence both hold. If the same external blocker persists for three consecutive cycles, follow Codex’s blocked-goal policy. Escalate immediately for missing authority, credentials, risky external actions, or a decision that requires human judgment.

## Candidate improvement and selection

Use multiple candidate versions only when output quality is subjective, the alternatives are independent, and a comparison rubric can be stated. Keep an accepted baseline. For each candidate, apply the same gate and score against the user’s criteria; select the highest-scoring candidate that passes required gates. Do not use self-voting as a substitute for an objective gate, and do not generate candidates that would exceed a user-supplied budget.

For code, prefer one implementation plus an independent reviewer or verifier when available. For writing, design, or plans, compare at most the number of alternatives the user requests; otherwise use two only when the expected benefit justifies the added work.

## Boundaries

This skill is invoked as `$goal-loop-runner`. It does not add a native `/loop` command, a background daemon, or a timer. Recurring unattended execution must be run by an external scheduler that starts bounded Codex jobs and gives each job the same goal and state-file path.
