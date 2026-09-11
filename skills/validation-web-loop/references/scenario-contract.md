# Scenario and report contract

## Accepted scenario

A scenario is JSON with:

- `schemaVersion`, `id`, `title`, `description`, `revision`, and optional `tags`;
- a non-empty `testCases` array;
- for every case: a unique lowercase kebab-case `id`, `title`, `priority`, non-empty `preconditions`, non-empty `steps`, `expectedResult`, and non-empty `tags`.

Treat the revision as immutable execution provenance. If the stored scenario changes, generate or select a new executor revision before claiming that the new cases ran.

Cases describe observable behavior, not implementation wishes. Do not invent a successful API, selector, credential, tenant configuration, or role merely to make a case executable. Put external requirements in preconditions and classify unavailable requirements as `BLOCKED`.

Coverage should include only applicable state boundaries, but must not hide them inside one happy-path case. Consider pre-session inputs, reload/navigation persistence, fresh-page restore, streaming/progress completion, denial or cancellation of a proposed write, and cleanup of validation-only state. A denial/cancel case asserts that the persistent side effect did not occur; it never authorizes that effect.

## Environment adapter

An adapter supplies application-specific rules the scenario must not guess:

- matching read-only authentication or production baseline, when required;
- local route and service readiness proof;
- allowed test data and mutation allowlist;
- source-reflection, feature-flight, or tenant gates;
- managed-process ownership and cleanup;
- failure artifacts and redaction rules.

When an adapter conflicts with generic guidance, the adapter wins for its application. If no adapter is declared, establish equivalent boundaries with the user before any external mutation.

## Evidence rules

Evidence must be independent of agent opinion. Useful proof includes an accessibility snapshot, exact route/state assertion, response status, network request, console record, persisted artifact, revision, or service readiness endpoint. A screenshot supplements but does not replace semantic assertions.

The connected page has one browser writer at a time. Cases that navigate or interact with the same page execute serially; only non-browser evidence collection may run in parallel. Application protocol or streaming evidence belongs to a reviewed environment adapter or executor extension, not arbitrary case JavaScript.

Never store credentials, tokens, cookies, tenant-private payloads, or unredacted personal data in reports. Record only the minimum route and request details needed to prove the assertion.

## Result model

- `PASS`: all assertions in the case passed with fresh evidence.
- `FAIL`: the application behavior contradicted an assertion and evidence was captured.
- `BLOCKED`: an authentication, authorization, credential, service, flight, environment, or test-data prerequisite prevented the assertion.
- `SKIPPED`: the case does not apply to the selected branch or was excluded before execution with a stated reason.

A blocked prerequisite is not a product failure. A dependent case inherits neither `PASS` nor `FAIL`; report it separately as blocked or skipped according to the scenario.

## Report

Return:

1. scenario ID, title, and revision;
2. adapter and browser-control surface;
3. preflight and mutation-boundary verdicts;
4. ordered case results with case ID, verdict, assertions, evidence paths, and duration when available;
5. totals by verdict;
6. recovered attempts and changed actions;
7. unresolved external prerequisites;
8. regression findings and the smallest evidence-backed next development action.

The report is complete only when every selected case has a terminal verdict and referenced artifacts exist.

When comparing with a previous report, require the same scenario revision, assertion contract, adapter, environment, and material role/flight state. Compare stable case IDs and preserve non-comparable or incomplete baselines as historical context rather than treating them as a clean run.
