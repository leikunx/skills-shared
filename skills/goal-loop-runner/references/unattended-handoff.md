# Unattended Handoff Protocol

Read this reference only when the user says they will be asleep, away, or unavailable for a stated pursuit window.

## Before the window

Send one consolidated preflight message containing:

1. The six-part goal contract.
2. Every material question whose answer would change the objective, verification method, authority, safety, or external impact.
3. The proposed start/end time and timezone, exact scheduler command or definition and identifier, cadence, maximum jobs or rounds, per-job timeout, state path, and objective gate.
4. The non-overlap lease and stale-claim recovery policy, plus ownership of process shutdown and log cleanup.
5. Any external prerequisite already known to require the user.

Do not scatter clarification across multiple turns. If no material question remains, say so explicitly. Do not start scheduled unattended work until the user confirms the contract or explicitly tells you to begin.

## During the window

- Use an external scheduler for bounded jobs that share the same goal and state path. An inactive chat turn is not a continuous worker.
- Persist the exact scheduler command or definition, scheduler id, current job id, per-job timeout, and log location so another run can inspect or resume it.
- Prevent overlapping jobs against the same mutable target unless concurrent execution is explicitly safe. Acquire one time-bounded round lease in goal state before acting and release it on exit.
- Treat a lease as stale only after its expiry and a fresh check confirms that the recorded process, browser action, or external operation is no longer active. Record reclamation evidence before starting another mutation.
- At the start of each job, inspect the latest real environment state and rebuild the round packet from the original contract, accepted checkpoint, evidence, remaining work, and latest failure.
- Attempt one dominant state transition, then perform a separate verification pass. Only verified state enters the accepted checkpoint.
- Do not ask the unavailable user routine questions. Use discoverable facts and already-authorized safe defaults.
- When a genuine user-only prerequisite appears, record it and the minimum answer or action needed, continue independent safe work, and recheck it on later scheduled jobs. Never invent approval, credentials, authentication, payment consent, or a product decision.
- For browser work, use Playwright Extension MCP when available and collect fresh page evidence. For non-browser work, run the relevant tests, build, lint, data, artifact, or service-readiness gates.
- After a recoverable failure, choose a materially different diagnostic or repair. Do not repeat an unchanged action merely to stay busy.
- Each job owns processes it starts. Record their handles and readiness/log evidence, then stop or hand them off explicitly before the lease ends. Never stop an unowned process.

At the window end, stop scheduling new work and report the accepted checkpoint, objective-gate evidence, rejected or recovered attempts, unresolved external prerequisites, and the exact next action.

## Reusable English prompt

```text
I am going to sleep and will return in 12 hours.

Before the unattended window begins, review my request and send me one consolidated message containing the proposed goal contract, every material question that would change the objective, verification method, authority, safety, or external impact, and the planned window end time, timezone, exact scheduler command or definition, scheduler identifier, cadence, maximum jobs or rounds, per-job timeout, state path, verification gate, non-overlap lease/stale-recovery policy, and process/log cleanup owner. Do not begin unattended execution until I answer those questions or explicitly tell you to proceed.

After I confirm the contract or tell you to begin, pursue the goal throughout the 12-hour window using bounded, scheduler-backed jobs that share the same durable goal state. Do not claim that one inactive chat turn can work continuously. Prevent overlapping mutations with a time-bounded round lease. Reclaim an expired lease only after checking that the recorded process or external action is no longer active. Do not pause scheduled work to ask me routine questions, because I will be unavailable. Resolve ordinary implementation choices from existing evidence and already-authorized safe defaults.

Each job must record its scheduler/job id, timeout, lease, started processes, and log path; read the latest state; inspect the real environment; choose one bounded action; execute it; and run an objective verification gate before accepting progress. Preserve the last verified checkpoint. Treat failed, partial, timed-out, or self-reported output as evidence for recovery, not as completed work. After a failure, try a materially different safe diagnostic or recovery action rather than repeating the same attempt. Stop or explicitly hand off every process the job owns before releasing its lease.

For web browsing, browser automation, or web testing, use the Playwright Extension MCP whenever it is available. For all other work, run the appropriate tests, builds, lint checks, data checks, visual inspections, or service-readiness checks.

If progress requires credentials, interactive sign-in, multifactor approval, payment confirmation, destructive authority, or a material product decision that only I can provide, do not guess or bypass it. Record the exact evidence and minimum unblocking action, continue any independent safe work, and revalidate the prerequisite in later jobs until the window ends.

When the 12-hour window ends, stop scheduling new work and give me an evidence-backed report of what is complete, what failed and recovered, what remains blocked or unverified, and the exact next action.

Before I go offline, do you have any material questions?
```
