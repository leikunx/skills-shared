# Review lenses and finding contract

Use this reference selectively. A focused request may need only one or two lenses.

## Lenses

### Boundaries and dependency direction

- Locate entrypoints, public interfaces, storage and network seams, and cross-package calls.
- Check whether dependency direction matches ownership and lifecycle boundaries.
- Distinguish an actual cycle or leaky abstraction from superficial file placement.

### Cohesion and change amplification

- Trace how a representative behavior changes across files and packages.
- Look for duplicated policy, divergent implementations, hidden temporal coupling, or one module with unrelated reasons to change.
- Counter-check whether duplication is deliberate isolation for compatibility, performance, or deployment.

### Testability and failure containment

- Map critical behavior to observable tests, including error and recovery paths.
- Check whether time, randomness, concurrency, I/O, and global state are controllable at a boundary.
- Do not equate line coverage with behavioral protection.

### Production readiness

- Inspect timeout, cancellation, retry, idempotency, resource cleanup, backpressure, data validation, observability, and degraded-mode behavior where relevant.
- Require a concrete request path or failure mode; avoid generic scale warnings.

### Regression and decision history

- Use blame, commits, reverted changes, issues, and architecture records to identify constraints and recurring failures.
- History explains intent but does not override current executable evidence.

## Finding record

```text
ID / status:
Claim:
Receipts:
Impact path:
Counter-search:
Blast radius:
Compatibility constraints:
Smallest correction:
Verification gate:
Residual uncertainty:
```

Statuses:

- `verified`: direct executable or historical evidence establishes the claim.
- `supported`: multiple relevant receipts converge, with a stated remaining limit.
- `inferred`: evidence supports the explanation but does not directly prove it.
- `unresolved`: material evidence is absent or conflicting; do not place in the committed refactor plan.
