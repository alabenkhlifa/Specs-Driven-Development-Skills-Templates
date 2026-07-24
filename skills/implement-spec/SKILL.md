---
name: implement-spec
description: Implement and verify one approved Spec-Driven Development slice from requirements.md, design.md, and tasks.md. Use when a user asks to build an approved feature slice, continue its active tasks, or complete its verification gate while preserving scope, stop conditions, progress logs, and specification write-back.
---

# Implement Spec

Implement only the active approved slice and preserve the agreement around it.

## Preconditions

Confirm that expected behavior, design decisions, implementation boundary, task proof, and project checks are clear. Stop and use `update-spec` when a decision blocks active implementation or required verification. A later deployment or release gate is not an implementation stop condition unless the requested work would cross that gate.

## Workflow

1. Read the applicable `AGENTS.md` and all three feature specification files.
2. Inspect relevant existing code and confirm ownership boundaries.
3. Confirm that unresolved items name the stage they block. Keep explicit deployment-only gates visible without treating them as active implementation blockers.
4. Mark the active task `In Progress`.
5. Implement one task at a time and run its attached proof.
6. Write progress, failures, discoveries, and deferred work into `tasks.md` as state changes.
7. Stop and use `update-spec` when behavior, design, scope, or blocker classification must change.
8. Run the complete verification gate.
9. Mark the slice `Verified` only when every required check passes, and report release readiness separately.

## Stop Conditions

Stop when work expands beyond the approved boundary, a missing decision affects behavior or architecture required by the active slice, implementation conflicts with the specification, a required check fails outside the slice, or ownership overlaps another task or agent.

Do not stop implementation only because a recorded deployment or release gate remains incomplete. Do stop before deploying, releasing, or claiming release readiness while that gate remains incomplete.

Use sub-agents only when work separates cleanly by ownership, files, and proof. Reconcile all results and run final verification in one place.

## Boundaries

- Do not implement unapproved scope.
- Do not change acceptance criteria to fit code.
- Do not hide failing checks or unresolved decisions.
- Do not mark work complete without its proof.
- Do not describe verified implementation as deployable or releasable unless its release gates also pass.

## Completion

Finish when approved behavior works, required checks pass, the specification files reflect the final implementation state, and any remaining release gate is reported explicitly.
