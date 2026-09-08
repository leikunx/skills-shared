---
name: architecture-health-review
description: Review a codebase or component for evidence-backed architecture, maintainability, testability, and production-readiness risks. Use for architecture-health and technical-debt assessments; do not use for implementing an already-decided refactor or ordinary code review.
---

# Architecture Health Review

Produce a review whose findings can survive implementation planning. Inspect broadly, but report only risks supported by repository evidence and a credible impact path.

## Scope and authority

Resolve the requested component and review focus from the user. If scope is omitted, select one significant production component using repository manifests and entrypoints, and state that assumption. Treat an all-repository review as a separate large scope; do not silently fan out across every package.

The default deliverable is read-only analysis. Do not edit code, create issues, open pull requests, or start a refactor unless the user requests that additional outcome.

## Establish the baseline

Read applicable repository instructions, manifests, architecture decisions, public interfaces, and the component's tests. Identify the real dependency and execution boundaries from code. Discover quality commands from project configuration, but run only the smallest non-mutating checks needed to test a finding.

Read [review-lenses.md](references/review-lenses.md) for the lenses and finding contract. Apply only the lenses relevant to the requested focus.

## Evidence protocol

For every candidate finding:

1. State what would be observable if the risk is real and what would distinguish an intentional design.
2. Gather a receipt from executable code, dependency edges, tests, build configuration, or version-control history. Documentation alone is context, not proof of runtime behavior.
3. Search for disconfirming evidence such as another caller, a boundary test, a documented compatibility constraint backed by code, or a recent fix.
4. Trace affected callers, data, interfaces, and validation surfaces before proposing a change.
5. Assign `verified`, `supported`, `inferred`, or `unresolved` from the evidence—not a numerical confidence guess.

Exclude a claim when its only support is a code-smell label, duplicated reviewer opinion, or an assumed best practice. Keep unresolved risks separate from accepted findings and name the evidence that would resolve them.

## Synthesis

Group surviving findings by root cause rather than emitting one item per symptom. Lead with the highest-impact verified risk. Each reported item must contain:

- stable identifier and concise title;
- evidence receipts with file paths and line numbers or commit identifiers;
- violated behavior or operational consequence;
- counter-evidence checked and its result;
- blast radius and compatibility constraints;
- smallest plausible correction;
- tests or observations that would prove the correction.

Also list rejected candidates when their rejection prevents future reviewers from repeating the same false positive. State inspected areas and material areas not inspected so a narrow report is not mistaken for complete repository coverage.

If implementation is requested, preserve this report as the acceptance baseline, change one coherent root cause at a time, and rerun the affected gate after each change. A successful build alone does not resolve an architectural finding unless it exercises the claimed boundary.

## Provenance

This Codex adaptation was independently written from general evidence and counter-search methods reviewed during a private internal skill-corpus intake. Detailed source provenance remains in the non-public migration audit; no internal topology, identifiers, or source prose is included here.

## Evolution Contract

Record task-local outcomes in the active goal state, not in this skill. Keep proposed improvements separate from validated lessons. Update this skill or its references only after a later run proves an objective improvement or establishes a stable safety or operational invariant. For every self-update, record the trigger, exact change, evidence, scope, and rollback condition, then validate the changed skill before relying on it. This contract does not expand authorization or permit unrelated changes.
