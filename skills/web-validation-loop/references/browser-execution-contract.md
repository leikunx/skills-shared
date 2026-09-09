# Browser execution contract

Use this contract for scenario execution. Application-specific adapters may tighten it but must not weaken authorization, evidence, or cleanup boundaries.

## Browser ownership

Treat each connected page or context as a mutable shared resource. Exactly one executor owns navigation and interaction at a time. Do not run browser-writing agents or cases in parallel against the same page; clicks, dialogs, tabs, history, storage, and event buffers can clobber one another. Read-only source, release, or log analysis may run concurrently because it cannot change browser state.

Record the owning run, page/tab, starting route, and expected cleanup. If ownership is lost or the page is changed outside the run, restore a known state and recheck preconditions before continuing. Never attach new observations to an earlier case merely because the same conversation or tab still exists.

## Case state

Unless the scenario declares a dependency, each case starts from the adapter's known route and establishes its own preconditions. A dependency states which earlier behavior is required; it is not permission to rely on undocumented residue.

When relevant, author separate cases for:

- data or files supplied before the session or page flow starts;
- reload and navigation persistence;
- session, task, or draft restore in a fresh page or tab;
- cleanup and restoration of validation-only state.

Use stable identifiers and final-state reads so a restored UI is tied to the same underlying object rather than a visually similar replacement.

## Evidence surfaces

Accessibility snapshots and observable assertions are the default evidence. Add another surface only when it distinguishes the behavior under test:

| Surface | Use |
| --- | --- |
| Screenshot | Visual layout or a failure that semantic evidence cannot convey; supplementary, never the sole behavioral oracle. |
| Console/network metadata | A failed resource, navigation, or client error; bound collection size and remove query strings, headers, bodies, cookies, and credentials. |
| Streaming/protocol events | Progress, event ordering, tool traces, or completion semantics; the adapter defines a reviewed bounded observer and stable fields. |
| Persisted artifact | File, saved setting, task, or backend state; re-read through an authoritative surface and compare identity/content. |

Do not inject an application-specific interceptor as generic JavaScript. Add protocol capture through a reviewed executor or adapter, clear its buffer before each case, and include only the event fields needed by declared assertions.

## Safe write-boundary cases

Coverage approval and mutation permission are separate. A denial or cancellation case may exercise an approval surface without granting the underlying write. Assert both the visible denial/cancel result and absence of the persistent side effect. Never relabel Save, Send, Create, Delete, or Approve as a UI-only action to bypass authorization.

## Failures and baselines

Browser disconnection, executor failure, missing prerequisites, and product assertion failures are distinct outcomes. Preserve every selected case in the report; use `BLOCKED` or the workflow's unexecuted status rather than inventing a product result.

A baseline is comparable only when scenario revision, assertion contract, adapter, environment, and material role/flight state match. Compare by stable case ID and report status transitions, regressions, recoveries, added/removed cases, and incomplete runs. A stale or mismatched baseline remains historical context, not pass/fail evidence.
