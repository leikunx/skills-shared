# Goal Loop Runner Evolution Log

This log records user-directed operating requirements and reusable improvements that have objective evidence or are stable safety/operational invariants. Per-goal hypotheses and one-off workarounds remain in the selected goal state's iteration log.

## 2026-09-09 — Profile-aware browser instance selection

- **Trigger:** The user established that separate Playwright Extension MCP instances normally use different authenticated profiles and requested local account mappings with general shared guidance.
- **Exact change:** Added instance selection by explicit user choice, task account context, and project mapping; live identity checks for account-sensitive actions; goal-state evidence; separation of browser and non-browser authentication; and local storage of exact mappings. Recovery must preserve the intended identity and authorization boundary.
- **Evidence:** Two distinct Playwright Extension MCP namespaces were available, and the user explicitly supplied their usual profile roles. The prior browser default covered tool availability but did not explain selection between authenticated instances. This is a user-established operational invariant, not a claim that a remembered mapping proves live authentication.
- **Scope:** Browser iterations with multiple instances or account-sensitive work. Exact account names and machine-specific mappings remain in project memory; no new external authority or mandatory browser work for non-browser tasks is added.
- **Rollback condition:** If this guidance causes unnecessary identity prompts for public browsing or conflicts with an explicit instance choice, narrow checks to account-sensitive actions while preserving the requested instance. Correct stale mappings in project memory rather than hard-coding replacements into this shared skill.

## 2026-09-07 — Verified round packets and unattended handoff

- **Trigger:** The user asked for a deep review of AMAP-ML/LongHorizon-Harness and an English, reusable version of a 12-hour sleep-window instruction.
- **Exact change:** Added a compact round packet reconstructed from the original contract, accepted checkpoint, evidence, remaining work, failures, and user amendments; separated attempt, mutation-free verification, and checkpoint promotion; labeled failed/partial/self-reported output as untrusted until verified; strengthened bounded single-transition rounds and full-contract completion checks. Expanded unattended pursuit with one consolidated pre-window clarification, accepted-checkpoint recovery, no blocking mid-window questions, and scheduler identity/command, per-job timeout, non-overlap lease, stale-claim recovery, and process/log cleanup ownership. Added `references/unattended-handoff.md` with the polished English prompt.
- **Evidence:** LongHorizon-Harness commit `a1dd930` and its paper model task execution as explicit state management: fresh-context executors act on one bounded subtask, read-only auditors inspect real environment state, and only audited facts update the ledger. Its code rejects completion without a complete/clean/aligned audit, restores state/contract/audit history on resume, and preserves timeout output as recovery evidence. Thirteen platform-neutral prompt-contract tests passed locally. Native-Windows resume/hardening tests failed because the upstream secure no-follow filesystem primitive is unavailable, so the runtime itself was not adopted; the skill keeps its existing external-scheduler abstraction. An independent realistic sleep-window forward test found the first revision safe but underspecified scheduler command, timeout, identity/lease, stale recovery, and cleanup fields; the second revision added those fields.
- **Scope:** Applies to long-horizon and explicitly unattended goal runs. A separate verifier is preferred for complex or consequential work but is not mandatory when unavailable; the same agent may perform a dedicated no-mutation verification pass. This adds no authority and does not turn an inactive chat into a daemon.
- **Rollback condition:** If the added trust bookkeeping consumes disproportionate effort on short tasks, narrow it to tasks spanning multiple material cycles. If scheduler jobs overlap, duplicate mutations, or increase cost without objective-gate gains, retain the checkpoint model but reduce cadence/round count and require a single active job.

## 2026-09-01 — Final-deliverable ownership and validated evolution

- **Trigger:** The user established that they will specify the final deliverable, while the agent must autonomously pursue it through repeated, evidence-backed attempts rather than ending at the first failure.
- **Exact change:** Added the `Final-deliverable ownership` policy: recoverable failure is an iteration result; choose a materially different next action; rerun the objective gate; do not conclude while a credible safe action remains. Added the rule to update only the smallest relevant skill/reference after later validation or a user-established invariant.
- **Evidence:** The prior skill required individual iterations and recovery but did not explicitly prohibit finalizing on a repairable failed attempt or direct the agent to update relevant reusable guidance from a validated gap.
- **Scope:** Applies to goal-driven work only. It does not authorize new external actions, broaden permissions, or replace the three-cycle external-blocker policy.
- **Rollback condition:** If the policy causes unbounded work, repeated unchanged actions, or a safety/authorization conflict, retain the existing blocked-stop rules and narrow the policy to the affected goal type after evidence review.

## 2026-09-01 — Speech-to-text interpretation default

- **Trigger:** The user established that their messages are voice input transcriptions and can contain recognition errors, repetitions, and broken phrasing.
- **Exact change:** Added a preflight default to infer the coherent intended meaning using active-goal context and evidence, while treating the inference as an assumption and requesting one clarification only for materially different authority, outcome, verification, or risk interpretations.
- **Evidence:** This is an explicit user-established operating convention; the skill already recognized fuzzy and voice-transcribed input but did not make speech-to-text the default input model or specify what may be retained.
- **Scope:** Applies to interpretation before goal work. Confirmed corrections are task facts in goal state; only the stable convention is reusable guidance. It does not authorize an inferred external action or change a safety boundary.
- **Rollback condition:** If the default repeatedly produces a material misinterpretation, restrict it to explicitly marked voice input and retain the clarification gate for consequential ambiguity.

## 2026-09-03 — User-directed unattended pursuit windows

- **Trigger:** The user established a stable operating requirement: when they invoke this skill while away or asleep for a long period, the agent should continue safe, evidence-driven exploration through recoverable browser and process failures instead of ending at the first interruption.
- **Exact change:** Added `Unattended pursuit windows`: record a stated execution window and cadence; use an external scheduler for bounded jobs that share goal state; require fresh browser/process/remote inspection and a materially different recovery action after failure; keep observing genuine external prerequisites without bypassing authentication, credentials, payment confirmation, or other authorization.
- **Evidence:** The existing skill already required evidence-driven iterations and a scheduler for recurring work, but lacked an explicit unattended-window policy or concrete recovery choices for a disconnected browser/session. This user-established requirement fills that operational gap while retaining existing blocked and authorization rules.
- **Scope:** Applies only when the user explicitly requests unattended pursuit. It does not create a daemon by itself, authorize external mutations, accept charges, or override user authentication.
- **Rollback condition:** If scheduled jobs create unbounded cost, duplicate work, or repeatedly poll a prerequisite without a credible state change, retain the same state file but lengthen/disable the cadence and narrow the rule to the affected task type after evidence review.
