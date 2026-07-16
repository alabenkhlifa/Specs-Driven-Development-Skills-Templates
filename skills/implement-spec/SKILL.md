---
name: implement-spec
description: Implement and verify one approved Spec-Driven Development slice from requirements.md, design.md, and tasks.md. Use when a user asks to build an approved feature slice, continue its active tasks, or complete its verification gate while preserving scope, stop conditions, progress logs, and specification write-back.
---

# Implement Spec

Implement only the active approved slice and preserve the agreement around it.

## Preconditions

Confirm that expected behavior, design decisions, implementation boundary, task proof, and project checks are clear. Stop and use `update-spec` when a blocking decision is missing.

## Workflow

1. Read the applicable `AGENTS.md` and all three feature specification files.
2. Inspect relevant existing code and confirm ownership boundaries.
3. Mark the active task `In Progress`.
4. Implement one task at a time and run its attached proof.
5. Write progress, failures, discoveries, and deferred work into `tasks.md` as state changes.
6. Stop and use `update-spec` when behavior, design, or scope must change.
7. Run the complete verification gate.
8. Mark the slice `Verified` only when every required check passes.

## Stop Conditions

Stop when work expands beyond the approved boundary, a missing decision affects behavior or architecture, implementation conflicts with the specification, a required check fails outside the slice, or ownership overlaps another task or agent.

Use sub-agents only when work separates cleanly by ownership, files, and proof. Reconcile all results and run final verification in one place.

## Boundaries

- Do not implement unapproved scope.
- Do not change acceptance criteria to fit code.
- Do not hide failing checks or unresolved decisions.
- Do not mark work complete without its proof.

## Completion

Finish when approved behavior works, required checks pass, and the specification files reflect the final state.

