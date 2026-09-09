# Evolution log

## 2026-09-09 — Browser execution and evidence contract

- Trigger: Review of a mature browser-validation corpus exposed reusable session-ownership, multi-surface evidence, restore, baseline, and partial-failure methods missing from the generic executor guidance.
- Change: Added an exclusive browser-writer contract; conditional console/network/protocol/artifact evidence; persistence/restore and denial-path coverage; and compatible-baseline rules.
- Evidence: Pending final goal validation of generator tests, the skill validator, public-boundary scans, and the exact diff.
- Scope: `web-validation-loop` instructions, references, and generated executors only; no application-specific routes, events, or mutation authority.
- Rollback: Revert the goal's shared repository commit if validation fails or the new contract causes incompatible scenario execution.
