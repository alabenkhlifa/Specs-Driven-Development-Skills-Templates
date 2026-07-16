# Update Spec

## Purpose

Update an existing specification while preserving decisions that are still valid. Do not implement the change.

## Input

- Specification path or feature name
- New requirement, discovery, constraint, or decision
- Relevant current code and verification results

## Optional Plan Stage

Use a read-only planning mode when the update changes approved behavior, crosses components, invalidates an architecture decision, or has unclear consequences.

1. Read the current specification and inspect the affected system.
2. Identify which requirements, design decisions, tasks, and checks would change.
3. Compare options and their consequences.
4. Resolve blocking decisions with the engineer.
5. Produce an approved update proposal without editing files.
6. Return to a writable mode and run this workflow with the approved proposal.

Do not edit the specification or implementation while still in a read-only planning mode.

## Workflow

1. Read the current `requirements.md`, `design.md`, and `tasks.md`.
2. Inspect the code or failed check that triggered the update.
3. Classify the change as expected behavior, scope, business rule, technical decision, implementation boundary, or verification.
4. Explain the impact before editing files.
5. Update only the sections affected by the decision.
6. Keep related requirements, design choices, tasks, and checks aligned.
7. Record deferred or invalidated work in `tasks.md`.
8. Report what changed and whether implementation can continue.

## Status Rules

- Move the specification back to `Draft` or `Blocked` when the update introduces an unresolved decision.
- Keep or restore `Approved` only when changed behavior and design are clear enough to implement.
- Remove `Verified` when changed behavior is not proven by existing checks.

## Restrictions

- Do not implement the change.
- Do not rewrite unrelated parts of the specification.
- Do not remove a tradeoff without recording what replaced it.
- Do not change acceptance criteria only to make a failing implementation pass.
- Do not continue implementation while a blocking question remains.

## Completion

The workflow is complete when the changed decision is visible, affected files agree, and implementation state is accurate.

