# Flakiness classification

Classify by evidence, not keywords alone.

| Outcome | Supporting evidence | Disconfirming check |
| --- | --- | --- |
| Flaky | Same revision has both pass and fail outcomes; unrelated branches share a failure signature; failure changes with order, seed, timing, or concurrency. | Check whether the supposedly identical runs changed dependencies, fixtures, configuration, or product revision. |
| Deterministic regression | Failure begins at a specific change and repeats under the same inputs; assertion values follow changed behavior. | Run or inspect the parent revision and an unaffected target. |
| Infrastructure | Setup or many unrelated tests fail through the same runner, capacity, network, dependency, container, or port condition. | Reproduce the individual test in a healthy isolated environment. |
| Insufficient | Only one occurrence, incomplete logs, unknown revision, or no passing comparison exists. | Obtain the smallest missing run or metadata that separates the other outcomes. |

## Required receipts

- Cross-run claim: exact run/build identifiers and revisions.
- Pass-after-fail claim: both outcomes for materially identical code and configuration.
- Timing or race claim: the observed event ordering, timeout, seed, or scheduling condition.
- Change-correlated claim: introducing revision plus the changed behavior.
- Infrastructure claim: the shared setup failure and its affected scope.

## Fix-to-cause map

| Cause | Preferred correction |
| --- | --- |
| Polling or fixed sleep | Observable condition/event plus a bounded deadline |
| Real clock or randomness | Injected clock/RNG and fixed test inputs |
| Shared mutable state | Per-test instance, reset, or isolated process/resource |
| Unawaited asynchronous work | Structured task ownership and teardown |
| Order dependence | Explicit ordering contract or order-independent assertion |
| Port/path/name collision | Dynamically allocated unique resource |
| Eventually consistent external system | Contract-aware polling and a dedicated integration test boundary |

A passing retry is evidence, not a repair.
