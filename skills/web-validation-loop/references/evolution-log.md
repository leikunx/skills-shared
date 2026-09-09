# Evolution log

## 2026-09-09 — Browser execution and evidence contract

- Trigger: Review of a mature browser-validation corpus exposed reusable session-ownership, multi-surface evidence, restore, baseline, and partial-failure methods missing from the generic executor guidance.
- Change: Added an exclusive browser-writer contract; conditional console/network/protocol/artifact evidence; persistence/restore and denial-path coverage; and compatible-baseline rules.
- Evidence: The generated-skill Node test passes; `quick_validate.py` passes; reference, public-boundary, secret-literal, and exact-source-line scans pass. Final commit/diff evidence is retained in the active goal state.
- Scope: `web-validation-loop` instructions, references, and generated executors only; no application-specific routes, events, or mutation authority.
- Rollback: Revert the goal's shared repository commit if validation fails or the new contract causes incompatible scenario execution.
