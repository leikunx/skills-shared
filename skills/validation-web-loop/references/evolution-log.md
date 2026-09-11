# Evolution log

## 2026-09-09 — Browser execution and evidence contract

- Trigger: Review of a mature browser-validation corpus exposed reusable session-ownership, multi-surface evidence, restore, baseline, and partial-failure methods missing from the generic executor guidance.
- Change: Added an exclusive browser-writer contract; conditional console/network/protocol/artifact evidence; persistence/restore and denial-path coverage; and compatible-baseline rules.
- Evidence: The generated-skill Node test passes; `quick_validate.py` passes; reference, public-boundary, secret-literal, and exact-source-line scans pass. Final commit/diff evidence is retained in the active goal state.
- Scope: `validation-web-loop` instructions, references, and generated executors only; no application-specific routes, events, or mutation authority.
- Rollback: Revert the goal's shared repository commit if validation fails or the new contract causes incompatible scenario execution.

## 2026-09-11: Validation-first skill names

- Trigger: User established `validation-` as the naming prefix for validation skills.
- Change: Rename this skill to `validation-web-loop` and generate `validation-<scenario-id>` executors; recognize the legacy generator marker during authorized regeneration.
- Evidence: Generator test passes for the generated name/path, pinned scenario, legacy marker regeneration, and refusal to overwrite an unrecognized directory.
- Scope: Skill identity, invocation references, and generated executor names; browser execution and authorization boundaries are unchanged.
- Rollback: Revert this naming change if discovery or regeneration fails; preserve existing scenario artifacts.
